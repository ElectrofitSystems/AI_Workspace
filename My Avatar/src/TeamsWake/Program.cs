using System.Text.Json;
using Windows.ApplicationModel;
using Windows.UI.Notifications;
using Windows.UI.Notifications.Management;

namespace TeamsWake;

internal static class Program
{
    [STAThread]
    static int Main(string[] args)
    {
        if (args.Length == 1 && (args[0] == "--signal-test" || args[0] == "--stop" || args[0] == "--show"))
        {
            try
            {
                using var signal = EventWaitHandle.OpenExisting(args[0] switch {
                    "--stop" => ListenerForm.StopSignal, "--show" => ListenerForm.ShowSignal, _ => ListenerForm.TestSignal });
                signal.Set();
                return 0;
            }
            catch (WaitHandleCannotBeOpenedException) { return 2; }
        }
        if (args.Length == 2 && args[0] == "--self-test")
        {
            Directory.CreateDirectory(args[1]);
            try
            {
                File.WriteAllText(Path.Combine(args[1], "result.json"), JsonSerializer.Serialize(EventQueue.SelfTest(Path.Combine(args[1], "queue"))));
                return 0;
            }
            catch (Exception ex) { File.WriteAllText(Path.Combine(args[1], "error.txt"), ex.ToString()); return 1; }
        }
        if (args.Length == 2 && args[0] == "--probe")
        {
            string? package = null, error = null, access = null;
            int? notificationCount = null, teamsCount = null;
            object? apps = null;
            try { package = Package.Current.Id.FullName; } catch { /* Unpackaged diagnostic. */ }
            try
            {
                var probeListener = UserNotificationListener.Current;
                access = probeListener.GetAccessStatus().ToString();
                if (probeListener.GetAccessStatus() == UserNotificationListenerAccessStatus.Allowed)
                {
                    var snapshot = probeListener.GetNotificationsAsync(NotificationKinds.Toast).AsTask().GetAwaiter().GetResult();
                    notificationCount = snapshot.Count;
                    teamsCount = snapshot.Count(n => EventQueue.IsTeams(n.AppInfo.AppUserModelId, n.AppInfo.DisplayInfo.DisplayName));
                    apps = snapshot.GroupBy(n => new { appId = n.AppInfo.AppUserModelId, appName = n.AppInfo.DisplayInfo.DisplayName })
                        .Select(g => new { g.Key.appId, g.Key.appName, count = g.Count() }).ToArray();
                }
            }
            catch (Exception ex) { error = ex.ToString(); }
            File.WriteAllText(args[1], JsonSerializer.Serialize(new { package, access, notificationCount, teamsCount, apps, error }));
            return 0;
        }
        using var singleton = new Mutex(true, "Local\\TeamsWake.Listener.v1", out var first);
        if (!first) return 0;
        ApplicationConfiguration.Initialize();
        Application.Run(new ListenerForm(args.Contains("--background")));
        return 0;
    }
}

public sealed class ListenerForm : Form
{
    public const string TestSignal = "Local\\TeamsWake.Test.v1";
    public const string StopSignal = "Local\\TeamsWake.Stop.v1";
    public const string ShowSignal = "Local\\TeamsWake.Show.v1";
    readonly string dataPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "TeamsWake");
    readonly Label stateLabel = new() { AutoSize = true, MaximumSize = new Size(650, 0) };
    readonly Label countLabel = new() { AutoSize = true };
    readonly Button accessButton = new() { Text = "Consenti accesso alle notifiche", AutoSize = true };
    readonly NotifyIcon tray;
    readonly System.Windows.Forms.Timer timer = new() { Interval = 5000 };
    readonly EventQueue queue;
    readonly HashSet<string> seen = [];
    readonly EventWaitHandle testSignal = new(false, EventResetMode.AutoReset, TestSignal);
    readonly EventWaitHandle stopSignal = new(false, EventResetMode.AutoReset, StopSignal);
    readonly EventWaitHandle showSignal = new(false, EventResetMode.AutoReset, ShowSignal);
    RegisteredWaitHandle? testRegistration, stopRegistration, showRegistration;
    UserNotificationListener? listener;
    bool subscribed, baselineReady, scanning, exiting;
    int queued, notificationCount, teamsCount;
    string access = "Non verificato", mode = "Avvio", package = "Assente", lastError = "";

    public ListenerForm(bool background)
    {
        Directory.CreateDirectory(dataPath);
        queue = new EventQueue(Path.Combine(dataPath, "pending"));
        Text = "Teams Wake — listener locale";
        ClientSize = new Size(740, 390);
        MinimumSize = new Size(620, 430);
        StartPosition = FormStartPosition.CenterScreen;
        if (background) { Opacity = 0; ShowInTaskbar = false; }
        Font = new Font("Segoe UI", 10);
        var panel = new FlowLayoutPanel { Dock = DockStyle.Fill, FlowDirection = FlowDirection.TopDown,
            WrapContents = false, Padding = new Padding(24), AutoScroll = true };
        panel.Controls.Add(new Label { Text = "Teams Wake", Font = new Font(Font.FontFamily, 20, FontStyle.Bold), AutoSize = true });
        panel.Controls.Add(new Label { Text = "Ascolta le notifiche Windows di Teams e salva gli eventi sul PC.", AutoSize = true });
        panel.Controls.Add(stateLabel);
        panel.Controls.Add(countLabel);
        panel.Controls.Add(new Label { Text = "Risveglio ChatGPT: NON COLLEGATO. Nessun messaggio viene inviato.\nIl test sintetico verifica soltanto la coda locale.", AutoSize = true, Margin = new Padding(0, 12, 0, 12) });
        panel.Controls.Add(accessButton);
        var testButton = new Button { Text = "Genera evento di prova locale", AutoSize = true };
        panel.Controls.Add(testButton);
        var hideButton = new Button { Text = "Continua in background", AutoSize = true };
        panel.Controls.Add(hideButton);
        var quitButton = new Button { Text = "Arresta ed esci", AutoSize = true };
        panel.Controls.Add(quitButton);
        Controls.Add(panel);
        var menu = new ContextMenuStrip();
        menu.Items.Add("Apri stato", null, (_, _) => { Show(); WindowState = FormWindowState.Normal; Activate(); });
        menu.Items.Add("Evento di prova locale", null, (_, _) => Synthetic());
        menu.Items.Add("Arresta ed esci", null, (_, _) => Exit());
        tray = new NotifyIcon { Icon = SystemIcons.Information, Text = "Teams Wake — avvio", ContextMenuStrip = menu, Visible = true };
        tray.DoubleClick += (_, _) => { Show(); WindowState = FormWindowState.Normal; Activate(); };
        accessButton.Click += async (_, _) => await RequestAccess();
        testButton.Click += (_, _) => Synthetic();
        hideButton.Click += (_, _) => Hide();
        quitButton.Click += (_, _) => Exit();
        timer.Tick += async (_, _) => await Scan();
        Shown += async (_, _) =>
        {
            if (background) { Hide(); Opacity = 1; ShowInTaskbar = true; }
            testRegistration = ThreadPool.RegisterWaitForSingleObject(testSignal, (_, _) => Dispatch(Synthetic), null, -1, false);
            stopRegistration = ThreadPool.RegisterWaitForSingleObject(stopSignal, (_, _) => Dispatch(Exit), null, -1, false);
            showRegistration = ThreadPool.RegisterWaitForSingleObject(showSignal, (_, _) => Dispatch(() => { Show(); WindowState = FormWindowState.Normal; Activate(); }), null, -1, false);
            await Initialize();
        };
        FormClosing += (_, e) => { if (!exiting) { e.Cancel = true; Hide(); } };
    }

    void Dispatch(Action action)
    {
        if (exiting || !IsHandleCreated) return;
        try { BeginInvoke(action); } catch (InvalidOperationException) { }
    }

    async Task Initialize()
    {
        try { package = Package.Current.Id.FullName; }
        catch { package = "Assente (esecuzione locale)"; }
        try
        {
            listener = UserNotificationListener.Current;
            access = listener.GetAccessStatus().ToString();
            if (listener.GetAccessStatus() == UserNotificationListenerAccessStatus.Allowed) await StartListening();
            else SetState("In attesa del consenso Windows");
        }
        catch (Exception ex) { SetState("Errore inizializzazione", ex.ToString()); }
    }

    async Task RequestAccess()
    {
        if (listener == null) { SetState("Installazione richiesta", "Installa e avvia la versione MSIX prima di richiedere l'accesso."); return; }
        accessButton.Enabled = false;
        try
        {
            var result = await listener.RequestAccessAsync(); // Called on the WinForms STA UI thread.
            access = result.ToString();
            if (result == UserNotificationListenerAccessStatus.Allowed) await StartListening();
            else SetState("Accesso non consentito", "Se già negato, l'accesso va abilitato manualmente nelle impostazioni Windows.");
        }
        catch (Exception ex) { SetState("Errore richiesta accesso", ex.ToString()); }
        finally { accessButton.Enabled = true; }
    }

    async Task StartListening()
    {
        if (listener == null) return;
        if (!subscribed)
        {
            try { listener.NotificationChanged += OnNotificationChanged; subscribed = true; }
            catch (Exception ex) { Log("NotificationChanged non disponibile: " + ex.ToString() + " HRESULT=0x" + ex.HResult.ToString("X8")); }
        }
        await Scan();
        timer.Start(); // Reconciliation also detects changes if the foreground callback is unavailable.
    }

    void OnNotificationChanged(UserNotificationListener sender, UserNotificationChangedEventArgs args)
    {
        Dispatch(async () => await Scan());
    }

    async Task Scan()
    {
        if (listener == null || scanning || exiting) return;
        scanning = true;
        try
        {
            var permission = listener.GetAccessStatus();
            access = permission.ToString();
            if (permission != UserNotificationListenerAccessStatus.Allowed)
            {
                baselineReady = false;
                SetState("Accesso revocato o non concesso");
                return;
            }
            var notifications = await listener.GetNotificationsAsync(NotificationKinds.Toast);
            if (exiting) return;
            notificationCount = notifications.Count;
            teamsCount = 0;
            var currentKeys = new HashSet<string>();
            foreach (var notification in notifications)
            {
                try
                {
                    var appId = notification.AppInfo.AppUserModelId;
                    var appName = notification.AppInfo.DisplayInfo.DisplayName;
                    if (!EventQueue.IsTeams(appId, appName)) continue;
                    teamsCount++;
                    var binding = notification.Notification.Visual.GetBinding(KnownNotificationBindings.ToastGeneric);
                    var text = binding?.GetTextElements().Select(t => t.Text).ToArray() ?? [];
                    var key = EventQueue.Key(appId, notification.Id, notification.CreationTime, text);
                    currentKeys.Add(key);
                    if (!baselineReady || seen.Contains(key)) continue;
                    if (queue.Enqueue(new("teams-wake/1", key, "teams.notification", DateTimeOffset.UtcNow,
                        notification.CreationTime, appId, appName, notification.Id, text, false)))
                    { queued++; Log("Evento Teams accodato " + key); }
                }
                catch (IOException) { throw; }
                catch (Exception ex) { Log("Notifica non leggibile: " + ex.Message); }
            }
            seen.Clear();
            seen.UnionWith(currentKeys);
            baselineReady = true;
            SetState(subscribed ? "Ascolto attivo + controllo ogni 5 secondi" : "Controllo notifiche ogni 5 secondi");
        }
        catch (Exception ex) { SetState("Errore acquisizione", ex.ToString()); }
        finally { scanning = false; }
    }

    void Synthetic()
    {
        try { queue.Enqueue(EventQueue.Synthetic()); queued++; Log("Evento sintetico accodato; risveglio assistente non collegato."); SetState(mode); }
        catch (Exception ex) { SetState("Errore coda", ex.ToString()); }
    }

    void SetState(string value, string error = "")
    {
        mode = value; lastError = error;
        stateLabel.Text = "Stato: " + mode + "\nPermesso notifiche: " + access +
            (error.Length == 0 ? "" : "\n" + error.Split('\n')[0]);
        countLabel.Text = $"Eventi accodati in questa sessione: {queued}";
        tray.Text = ("Teams Wake — " + mode)[..Math.Min(63, 13 + mode.Length)];
        var status = new { timestamp = DateTimeOffset.UtcNow, pid = Environment.ProcessId,
            mode, access, package, queued, notificationCount, teamsCount, eventCallback = subscribed,
            assistantWake = "NOT_CONFIGURED", lastError, dataPath };
        try
        {
            File.WriteAllText(Path.Combine(dataPath, "status.tmp"), JsonSerializer.Serialize(status, new JsonSerializerOptions { WriteIndented = true }));
            File.Move(Path.Combine(dataPath, "status.tmp"), Path.Combine(dataPath, "status.json"), true);
        }
        catch (Exception ex) { Log("Scrittura stato fallita: " + ex.Message); }
    }

    void Log(string message)
    {
        try
        {
            var path = Path.Combine(dataPath, "listener.log");
            if (File.Exists(path) && new FileInfo(path).Length > 1_000_000) File.Move(path, path + ".previous", true);
            File.AppendAllText(path, DateTimeOffset.UtcNow.ToString("O") + " " + message + Environment.NewLine);
        }
        catch { /* Do not crash the listener because diagnostic logging fails. */ }
    }

    void Exit()
    {
        exiting = true;
        testRegistration?.Unregister(null);
        stopRegistration?.Unregister(null);
        showRegistration?.Unregister(null);
        timer.Stop();
        if (subscribed && listener != null) listener.NotificationChanged -= OnNotificationChanged;
        SetState("Arrestato");
        tray.Visible = false;
        tray.Dispose();
        Close();
    }
}
