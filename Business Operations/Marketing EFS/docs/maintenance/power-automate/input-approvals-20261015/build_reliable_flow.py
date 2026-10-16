"""Build an unmanaged solution from the immutable exported Inputs flow.

Default package performs bootstrap/diagnostics only. --enable acquires/dispatches
new events; --confirm-status-contract is additionally required for actual creates
after REST diagnostics establish modern approval status 0=NotSubmitted.
No connection credentials or new approvers are added.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / "EFSMarketingApprovalReliability_1_0_0_3.zip"
SITE = "https://efitsys.sharepoint.com/sites/Documentation"
LIBRARY = "43a514e9-9126-4758-9383-cff80d269b5d"
QUEUE = "db240db6-c151-40f6-8851-3773be6091f3"
PREFIX = "/sites/Documentation/Shared Documents/General/Marketing/Inputs/"
QUEUE_API = f"_api/web/lists(guid'{QUEUE}')"
QUEUE_EXPR = QUEUE_API.replace("'", "''")
SOURCE_API = f"_api/web/lists(guid'{LIBRARY}')"
SOURCE_EXPR = SOURCE_API.replace("'", "''")
HOST = {
    "connectionName": "shared_sharepointonline",
    "operationId": "HttpRequest",
    "apiId": "/providers/Microsoft.PowerApps/apis/shared_sharepointonline",
}
SUCCESS = ["Succeeded"]
FAILURE = ["Failed", "TimedOut"]


def after(name=None, states=None):
    return {name: states or SUCCESS} if name else {}


def compose(value, previous=None):
    return {"type": "Compose", "inputs": value, "runAfter": after(previous)}


def expression_value(value):
    """Build typed WDL values; nested JSON payloads must stay escaped."""
    if isinstance(value, str) and value.startswith("@"):
        return value[1:]
    if isinstance(value, dict):
        expr = "json('{}')"
        for key, item in value.items():
            expr = f"setProperty({expr},'{key.replace(chr(39), chr(39)*2)}',{expression_value(item)})"
        return expr
    literal = json.dumps(value, ensure_ascii=False).replace("'", "''")
    return f"json('{literal}')"


def http(method, uri, body=None, previous=None, headers=None, retry=None):
    params = {"dataset": SITE, "parameters/method": method,
              "parameters/uri": uri,
              "parameters/headers": {"Accept": "application/json;odata=verbose",
                                     **(headers or {})}}
    if body is not None:
        params["parameters/headers"]["Content-Type"] = "application/json;odata=verbose"
        params["parameters/body"] = body if isinstance(body, str) else "@string(" + expression_value(body) + ")"
    return {"type": "OpenApiConnection", "runAfter": after(previous),
            "inputs": {"host": copy.deepcopy(HOST), "parameters": params,
                       "retryPolicy": retry or ({"type": "exponential", "count": 3,
                                                   "interval": "PT10S", "minimumInterval": "PT10S",
                                                   "maximumInterval": "PT1M"}
                                                  if method == "GET" else {"type": "none"})}}


def condition(expr, yes, no=None, previous=None):
    return {"type": "If", "expression": expr, "actions": yes,
            "else": {"actions": no or {}}, "runAfter": after(previous)}


def loop(items, actions, previous=None):
    return {"type": "Foreach", "foreach": items, "actions": actions,
            "runtimeConfiguration": {"concurrency": {"repetitions": 1}},
            "runAfter": after(previous)}


def merge_queue(row_id, state, payload, etag, previous=None):
    return http("POST", f"@concat('{QUEUE_EXPR}/items(',string({row_id}),')')",
                {"__metadata": {"type": "@body('Get_queue_metadata')?['d']?['ListItemEntityTypeFullName']"},
                 "DispatchState": state, "Payload": payload}, previous,
                {"X-HTTP-Method": "MERGE", "IF-MATCH": etag})


def queue_create(title, state, payload, previous=None):
    return http("POST", f"{QUEUE_API}/items",
                {"__metadata": {"type": "@body('Get_queue_metadata')?['d']?['ListItemEntityTypeFullName']"},
                 "Title": title, "DispatchState": state, "Payload": payload}, previous)


def make_definition(original, cutover, enable=False, confirm_status=False):
    definition = copy.deepcopy(original)
    definition["triggers"] = {
        "Every_five_minutes": {
            "type": "Recurrence", "recurrence": {"frequency": "Minute", "interval": 5},
            "runtimeConfiguration": {"concurrency": {"runs": 1, "maximumWaitingRuns": 1}}
        }
    }
    old_create = copy.deepcopy(next(a for a in original["actions"].values()
                                    if a.get("inputs", {}).get("host", {}).get("operationId") == "CreateApprovalRequest"))
    create = copy.deepcopy(old_create)
    params = create["inputs"]["parameters"]
    params["id"] = "@int(outputs('Read_payload')?['sourceId'])"
    params["approvalSchema/title"] = "Approva input | @{body('Fresh_source')?['d']?['FileLeafRef']}"
    params["approvalSchema/details"] = (
        "Valuta questo materiale per LinkedIn e newsletter.\n\n"
        "Documento: @{body('Fresh_source')?['d']?['FileLeafRef']}\n"
        "Apri materiale: https://efitsys.sharepoint.com@{body('Fresh_source')?['d']?['FileRef']}\n"
        "Revisione del riferimento: @{body('Fresh_source')?['d']?['OData__UIVersionString']}\n\n"
        "Scegli Approva o Rifiuta. Se è un collegamento, verifica l'originale e indica "
        "versione/data ed eventuali limiti d'uso nei commenti.\n\n"
        "L'approvazione riguarda il materiale verificato. La pubblicazione richiede un'autorizzazione distinta."
    )
    create["inputs"]["retryPolicy"] = {"type": "none"}
    create["runAfter"] = {}
    create.pop("metadata", None)

    actions = {
        "Configuration": compose({"EnableAcquisition": enable, "EnableDispatch": enable,
                                  "NativeStatusContractVerified": confirm_status,
                                  "BootstrapDiagnostics": not enable,
                                  "CutoverUtc": cutover, "SourceLibrary": LIBRARY,
                                  "QueueList": QUEUE, "Scope": "input-reference-review",
                                  "MaxDispatch": 3, "PacingSeconds": 30,
                                  "MaxAttempts": 5, "LeaseMinutes": 15}),
        "Get_queue_metadata": http("GET", f"{QUEUE_API}?$select=ListItemEntityTypeFullName", previous="Configuration"),
        "Get_queue_fields": http("GET", f"{QUEUE_API}/fields?$select=InternalName,TypeAsString,Indexed,EnforceUniqueValues", previous="Get_queue_metadata"),
        "Payload_fields": {"type": "Query", "inputs": {
            "from": "@body('Get_queue_fields')?['d']?['results']",
            "where": "@equals(item()?['InternalName'],'Payload')"}, "runAfter": after("Get_queue_fields")},
        "Ensure_payload_field": condition("@equals(length(body('Payload_fields')),0)", {
            "Create_payload_field": http("POST", f"{QUEUE_API}/fields",
                {"__metadata": {"type": "SP.FieldMultiLineText"}, "Title": "Payload",
                 "FieldTypeKind": 3, "RichText": False, "AppendOnly": False, "NumberOfLines": 6})},
            previous="Payload_fields"),
        "Title_fields": {"type": "Query", "inputs": {
            "from": "@body('Get_queue_fields')?['d']?['results']",
            "where": "@equals(item()?['InternalName'],'Title')"}, "runAfter": after("Ensure_payload_field")},
        "Ensure_title_index": condition("@not(equals(first(body('Title_fields'))?['Indexed'],true))", {
            "Index_title": http("POST", f"{QUEUE_API}/fields/getbyinternalnameortitle('Title')",
                {"__metadata": {"type": "SP.FieldText"}, "Indexed": True},
                headers={"X-HTTP-Method": "MERGE", "IF-MATCH": "*"})}, previous="Title_fields"),
        "Ensure_title_unique": condition("@not(equals(first(body('Title_fields'))?['EnforceUniqueValues'],true))", {
            "Unique_title": http("POST", f"{QUEUE_API}/fields/getbyinternalnameortitle('Title')",
                {"__metadata": {"type": "SP.FieldText"}, "EnforceUniqueValues": True},
                headers={"X-HTTP-Method": "MERGE", "IF-MATCH": "*"})}, previous="Ensure_title_index"),
        "Read_cursor": http("GET", f"{QUEUE_API}/items?$filter=Title%20eq%20'__cursor__'&$top=1", previous="Ensure_title_unique"),
        "Ensure_cursor": condition("@equals(length(body('Read_cursor')?['d']?['results']),0)", {
            "Create_cursor": queue_create("__cursor__", "checkpoint",
                "@string(addProperty(addProperty(json('{}'),'lastId',0),'cutoverUtc',outputs('Configuration')?['CutoverUtc']))")}, previous="Read_cursor"),
        "Cursor": http("GET", f"{QUEUE_API}/items?$filter=Title%20eq%20'__cursor__'&$top=1", previous="Ensure_cursor"),
        "Bootstrap_diagnostics": condition("@equals(outputs('Configuration')?['BootstrapDiagnostics'],true)", {
            "Source_field_diagnostics": http("GET", f"{SOURCE_API}/fields?$select=InternalName,Title,TypeAsString&$filter=substringof('Approval',InternalName)"),
            "Source_item_diagnostics": http("GET", f"{SOURCE_API}/items(652)", previous="Source_field_diagnostics")}, previous="Cursor"),
    }

    # A page is committed only after every enqueue succeeded (or already existed).
    enqueue_actions = {
        "Queue_key": compose("@concat('43a514e9-9126-4758-9383-cff80d269b5d:',string(items('Acquire_page')?['Id']),':',coalesce(items('Acquire_page')?['OData__UIVersionString'],'unresolved'),':input-reference-review')"),
        "Queue_existing": http("GET", f"@concat('{QUEUE_EXPR}/items?$filter=Title%20eq%20%27',encodeUriComponent(outputs('Queue_key')),'%27&$top=1')", previous="Queue_key"),
        "Enqueue_if_missing": condition("@equals(length(body('Queue_existing')?['d']?['results']),0)", {
            "Queue_snapshot": compose({"sourceId": "@items('Acquire_page')?['Id']",
                                       "refVersion": "@items('Acquire_page')?['OData__UIVersionString']",
                                       "fileRef": "@items('Acquire_page')?['FileRef']",
                                       "name": "@items('Acquire_page')?['FileLeafRef']",
                                       "targetRevisionVerified": False,
                                       "scope": "input-reference-review", "attempts": 0,
                                       "acquiredAt": "@utcNow()"}),
            "Enqueue": queue_create("@outputs('Queue_key')", "@if(empty(items('Acquire_page')?['OData__UIVersionString']),'unknown','queued')", "@string(outputs('Queue_snapshot'))", "Queue_snapshot")}, previous="Queue_existing")
    }
    acquire = {
        "Poll_source": http("GET", "@concat('" + SOURCE_EXPR + "/items?$select=Id,FileRef,FileLeafRef,FSObjType,Created,OData__UIVersionString&$filter=Id%20gt%20',string(json(first(body('Cursor')?['d']?['results'])?['Payload'])?['lastId']),'%20and%20Created%20ge%20datetime%27',json(first(body('Cursor')?['d']?['results'])?['Payload'])?['cutoverUtc'],'%27%20and%20FSObjType%20eq%200%20and%20startswith(FileRef,%27/sites/Documentation/Shared%20Documents/General/Marketing/Inputs/%27)&$orderby=Id%20asc&$top=100')"),
        "Acquire_page": loop("@body('Poll_source')?['d']?['results']", enqueue_actions, "Poll_source"),
        "Commit_nonempty_page": condition("@greater(length(body('Poll_source')?['d']?['results']),0)", {
            "Commit_cursor": merge_queue("first(body('Cursor')?['d']?['results'])?['Id']", "checkpoint",
                "@string(setProperty(json(first(body('Cursor')?['d']?['results'])?['Payload']),'lastId',last(body('Poll_source')?['d']?['results'])?['Id']))",
                "@first(body('Cursor')?['d']?['results'])?['__metadata']?['etag']")}, previous="Acquire_page")
    }
    actions["Acquisition_enabled"] = condition("@equals(outputs('Configuration')?['EnableAcquisition'],true)", acquire, previous="Bootstrap_diagnostics")

    # Claim with the ETag from the queue page. One flow run + one loop iteration.
    fresh_uri = "@concat('" + SOURCE_EXPR + "/items(',string(outputs('Read_payload')?['sourceId']),')?$select=Id,FileSystemObjectType,FSObjType,FileRef,FileLeafRef,OData__UIVersionString,OData__ApprovalStatus')"
    lease_etag = "@items('Dispatch_rows')?['__metadata']?['etag']"
    queue_id = "items('Dispatch_rows')?['Id']"
    base_payload = "@string(setProperty(setProperty(setProperty(setProperty(outputs('Read_payload'),'attempts',add(int(coalesce(outputs('Read_payload')?['attempts'],0)),1)),'runRef',workflow()?['run']?['name']),'startedAt',utcNow()),'leaseExpiresAt',addMinutes(utcNow(),15)))"

    # Re-read leased row before each write to use its new ETag; don't use '*'.
    def finish(name, state, payload, previous=None):
        return {
            f"{name}_read": http("GET", f"@concat('{QUEUE_EXPR}/items(',string({queue_id}),')')", previous=previous),
            f"{name}_write": merge_queue(queue_id, state, payload,
                 f"@body('{name}_read')?['d']?['__metadata']?['etag']", f"{name}_read")
        }

    # MERGE normally has no body. Use the read after lease as the payload baseline.
    created_payload = "@string(setProperty(setProperty(setProperty(json(body('Leased_row')?['d']?['Payload']),'approvalResult',body('Create_native_approval')),'approvalId',coalesce(body('Create_native_approval')?['approvalId'],body('Create_native_approval')?['ApprovalId'])),'completedAt',utcNow()))"
    unknown_payload = "@string(setProperty(setProperty(setProperty(setProperty(json(body('Leased_row')?['d']?['Payload']),'error',string(result('Create_scope'))),'retryAfterRaw',coalesce(outputs('Create_native_approval')?['headers']?['Retry-After'],'')),'nextAttemptAt',addSeconds(utcNow(),if(isInt(string(coalesce(outputs('Create_native_approval')?['headers']?['Retry-After'],''))),max(30,int(outputs('Create_native_approval')?['headers']?['Retry-After'])),add(int(createArray(30,60,120,240,480,960)[min(5,int(json(body('Leased_row')?['d']?['Payload'])?['attempts']))]),rand(0,16))))),'reconcileRequired',true))"
    create_scope = {"type": "Scope", "actions": {"Create_native_approval": create}, "runAfter": {}}
    create_branch = {"Create_scope": create_scope}
    create_branch["Verify_created_result"] = condition(
        "@not(empty(coalesce(body('Create_native_approval')?['approvalId'],body('Create_native_approval')?['ApprovalId'])))",
        finish("Created", "approval_created", created_payload),
        finish("Empty_result", "unknown", "@string(setProperty(setProperty(json(body('Leased_row')?['d']?['Payload']),'unverifiedApprovalResult',body('Create_native_approval')),'reconcileRequired',true))"),
        previous="Create_scope")
    failure_read = http("GET", f"@concat('{QUEUE_EXPR}/items(',string({queue_id}),')')")
    failure_read["runAfter"] = after("Create_scope", FAILURE)
    create_branch["Unknown_read"] = failure_read
    create_branch["Unknown_write"] = merge_queue(queue_id, "unknown", unknown_payload,
        "@body('Unknown_read')?['d']?['__metadata']?['etag']", "Unknown_read")
    # A pacing delay after either final state; one branch is skipped.
    create_branch["Pace_after_create"] = {"type": "Wait", "inputs": {"interval": {"count": 30, "unit": "Second"}},
        "runAfter": {"Verify_created_result": ["Succeeded", "Skipped"], "Unknown_write": ["Succeeded", "Skipped"]}}

    source_ok = {
        "Same_revision": condition("@and(not(empty(outputs('Read_payload')?['refVersion'])),equals(body('Fresh_source')?['d']?['OData__UIVersionString'],outputs('Read_payload')?['refVersion']),equals(coalesce(body('Fresh_source')?['d']?['FSObjType'],body('Fresh_source')?['d']?['FileSystemObjectType']),0),startsWith(coalesce(body('Fresh_source')?['d']?['FileRef'],''),'/sites/Documentation/Shared Documents/General/Marketing/Inputs/'))", {
            "Status_known": condition("@and(equals(outputs('Configuration')?['NativeStatusContractVerified'],true),not(equals(body('Fresh_source')?['d']?['OData__ApprovalStatus'],null)))", {
                "Not_submitted": condition("@equals(string(body('Fresh_source')?['d']?['OData__ApprovalStatus']),'0')", {
                    "Within_attempt_limit": condition("@lessOrEquals(int(json(body('Leased_row')?['d']?['Payload'])?['attempts']),outputs('Configuration')?['MaxAttempts'])", create_branch,
                        finish("Attempt_limit", "manual_review", "@string(setProperty(json(body('Leased_row')?['d']?['Payload']),'reason','Attempt limit reached; reconcile before further recovery'))"))},
                    finish("Existing", "existing_request", "@string(setProperty(json(body('Leased_row')?['d']?['Payload']),'observedNativeStatus',body('Fresh_source')?['d']?['OData__ApprovalStatus']))"))
            }, finish("Unconfirmed", "unknown", "@string(setProperty(json(body('Leased_row')?['d']?['Payload']),'reason','Native approval status contract absent or not verified'))"))
        }, finish("Superseded", "superseded", "@string(setProperty(json(body('Leased_row')?['d']?['Payload']),'reason','Source version/path changed'))"))
    }
    row_actions = {
        "Read_payload": compose("@json(items('Dispatch_rows')?['Payload'])"),
        "Lease_row": merge_queue(queue_id, "processing", base_payload, lease_etag, "Read_payload"),
        "Leased_row": http("GET", f"@concat('{QUEUE_EXPR}/items(',string({queue_id}),')')", previous="Lease_row"),
        "Fresh_source": http("GET", fresh_uri, previous="Leased_row"),
        "Validate_source": {"type": "Scope", "actions": source_ok, "runAfter": after("Fresh_source")},
        "Source_unavailable_read": http("GET", f"@concat('{QUEUE_EXPR}/items(',string({queue_id}),')')"),
    }
    row_actions["Source_unavailable_read"]["runAfter"] = after("Fresh_source", FAILURE)
    row_actions["Source_unavailable_write"] = merge_queue(queue_id,
        "@if(equals(outputs('Fresh_source')?['statusCode'],404),'source_missing','unknown')",
        "@string(setProperty(setProperty(json(body('Leased_row')?['d']?['Payload']),'sourceError',string(outputs('Fresh_source'))),'reconcileRequired',true))",
        "@body('Source_unavailable_read')?['d']?['__metadata']?['etag']", "Source_unavailable_read")
    dispatch = {
        "Expired_processing": http("GET", f"@concat('{QUEUE_EXPR}/items?$filter=DispatchState%20eq%20%27processing%27%20and%20Modified%20lt%20datetime%27',addMinutes(utcNow(),-15),'%27&$orderby=Id%20asc&$top=100')"),
        "Quarantine_expired": loop("@body('Expired_processing')?['d']?['results']", {
            "Expired_to_unknown": merge_queue("items('Quarantine_expired')?['Id']", "unknown",
                "@string(setProperty(setProperty(setProperty(json(items('Quarantine_expired')?['Payload']),'reason','Lease expired after interruption; reconcile before retry'),'reconcileRequired',true),'quarantinedAt',utcNow()))",
                "@items('Quarantine_expired')?['__metadata']?['etag']")}, "Expired_processing"),
        "Queued_rows": http("GET", f"{QUEUE_API}/items?$filter=DispatchState%20eq%20'queued'&$orderby=Id%20asc&$top=3", previous="Quarantine_expired"),
        "Dispatch_rows": loop("@body('Queued_rows')?['d']?['results']", row_actions, "Queued_rows")
    }
    actions["Dispatch_enabled"] = condition("@equals(outputs('Configuration')?['EnableDispatch'],true)", dispatch, previous="Acquisition_enabled")
    definition["actions"] = actions
    definition["outputs"] = {}
    return definition


def build(enable=False, confirm_status=False, cutover=None, output=None, rollback=False, version_override=None):
    cutover_path = HERE / "cutover.json"
    if cutover is None and cutover_path.exists():
        cutover = json.loads(cutover_path.read_text(encoding="utf-8"))["cutover_utc"]
    if cutover is None:
        cutover = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    datetime.strptime(cutover, "%Y-%m-%dT%H:%M:%SZ")
    if not cutover_path.exists():
        cutover_path.write_text(json.dumps({"cutover_utc": cutover, "note": "Initial poll cutoff fixed before import; do not reset on rebuild."}, indent=2)+"\n", encoding="utf-8")
    if rollback and (enable or confirm_status):
        raise ValueError("Rollback cannot enable the replacement workflow")
    version = "1.0.1.9" if rollback else ("1.0.1.1" if enable else "1.0.1.0")
    if version_override:
        if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+",version_override):
            raise ValueError("Version must contain four numeric components")
        version = version_override
    destination = Path(output) if output else HERE / f"EFSMarketingApprovalReliability_{version.replace('.', '_')}.zip"
    with zipfile.ZipFile(ORIGINAL) as source:
        if source.testzip():
            raise ValueError("Original archive CRC failed")
        workflow_name = next(n for n in source.namelist() if n.startswith("Workflows/") and n.endswith(".json"))
        workflow = json.loads(source.read(workflow_name))
        original_definition = copy.deepcopy(workflow["properties"]["definition"])
        if not rollback:
            workflow["properties"]["definition"] = make_definition(original_definition, cutover, enable, confirm_status)
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename == workflow_name and not rollback:
                    data = json.dumps(workflow, ensure_ascii=False, indent=2).encode("utf-8")
                elif item.filename == "solution.xml":
                    text = data.decode("utf-8")
                    data = re.sub(r"<Version>[^<]+</Version>", f"<Version>{version}</Version>", text, count=1).encode("utf-8")
                target.writestr(item, data)
    manifest = {"version": version, "package": destination.name, "cutover_utc": cutover,
                "acquisition_enabled": enable, "dispatch_enabled": enable,
                "native_status_contract_verified": confirm_status, "rollback_original_definition": rollback,
                "original_sha256": hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
                "package_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
                "workflow_file": workflow_name, "queue_id": QUEUE,
                "live_status": "pending_verification",
                "critical_assumptions": ["SharePoint HttpRequest parameters use parameters/* (connector schema must be validated live)",
                                         "REST returns verbose d/results and Id, OData__UIVersionString",
                                         "Native OData__ApprovalStatus contract must be verified from diagnostics before creates",
                                         "Unknown/processing rows are quarantined, not automatically resent",
                                         "No retroactive acquisition before persisted cutover",
                                         "Original archive and existing approvers/awaitAll unchanged"]}
    destination.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")
    return destination, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--confirm-status-contract", action="store_true")
    parser.add_argument("--cutover")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--rollback", action="store_true")
    parser.add_argument("--version", help="Explicit higher solution version for a verified correction")
    args = parser.parse_args()
    destination, manifest = build(args.enable, args.confirm_status_contract, args.cutover, args.output, args.rollback, args.version)
    print(json.dumps({"package": str(destination), **manifest}, indent=2))
