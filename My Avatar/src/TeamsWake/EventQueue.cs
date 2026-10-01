using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace TeamsWake;

public record WakeEvent(string Schema, string EventId, string Kind, DateTimeOffset ObservedAt,
    DateTimeOffset CreatedAt, string AppId, string AppName, uint NotificationId,
    string[] Text, bool Synthetic);

public sealed class EventQueue(string directory)
{
    public static bool IsTeams(string appId, string appName) =>
        appId.Equals("MSTeams_8wekyb3d8bbwe!MSTeams", StringComparison.OrdinalIgnoreCase) ||
        appName.Equals("Microsoft Teams", StringComparison.OrdinalIgnoreCase);

    public static string Key(string appId, uint id, DateTimeOffset createdAt, string[] text) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
            JsonSerializer.Serialize(new { appId, id, createdAt = createdAt.UtcTicks, text }))));

    public bool Enqueue(WakeEvent item)
    {
        Directory.CreateDirectory(directory);
        var destination = Path.Combine(directory, item.EventId + ".json");
        if (File.Exists(destination)) return false;
        if (Directory.EnumerateFiles(directory, "*.json").Take(2000).Count() >= 2000)
            throw new IOException("Coda piena (2000 eventi): acquisizione sospesa. Nessun consumatore configurato.");
        var temporary = destination + "." + Guid.NewGuid().ToString("N") + ".tmp";
        try
        {
            File.WriteAllText(temporary, JsonSerializer.Serialize(item, new JsonSerializerOptions { WriteIndented = true }));
            File.Move(temporary, destination);
            return true;
        }
        finally { if (File.Exists(temporary)) File.Delete(temporary); }
    }

    public static WakeEvent Synthetic() => new("teams-wake/1", Guid.NewGuid().ToString("N"),
        "test.wake", DateTimeOffset.UtcNow, DateTimeOffset.UtcNow, "TeamsWake.Test",
        "Teams Wake test", 0, ["Evento sintetico: verifica della coda locale, non del risveglio ChatGPT."], true);

    public static object SelfTest(string directory)
    {
        var queue = new EventQueue(directory);
        void Check(bool ok, string name) { if (!ok) throw new InvalidOperationException(name); }
        Check(IsTeams("MSTeams_8wekyb3d8bbwe!MSTeams", "altro"), "Teams app ID");
        Check(!IsTeams("browser", "Microsoft Edge"), "Filtro altre app");
        var now = DateTimeOffset.UtcNow;
        Check(Key("teams", 1, now, ["a"]) != Key("teams", 1, now.AddSeconds(1), ["a"]), "ID riutilizzato");
        Check(Key("teams", 1, now, ["a"]) != Key("teams", 1, now, ["b"]), "Notifica aggiornata");
        var item = Synthetic();
        Check(queue.Enqueue(item), "Scrittura iniziale");
        Check(!queue.Enqueue(item), "Deduplicazione");
        Check(!new EventQueue(directory).Enqueue(item), "Deduplicazione dopo riavvio");
        var roundTrip = JsonSerializer.Deserialize<WakeEvent>(File.ReadAllText(Path.Combine(directory, item.EventId + ".json")));
        Check(roundTrip?.EventId == item.EventId && roundTrip.Synthetic, "Formato evento");
        return new { passed = 8, eventFile = Path.Combine(directory, item.EventId + ".json"), assistantWake = "NOT_TESTED" };
    }
}
