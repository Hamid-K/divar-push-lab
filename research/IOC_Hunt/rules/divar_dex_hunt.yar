// Scan extracted classes*.dex files. APKs are ZIP containers; unpack them first.
// A YARA hit is a lead. Verify the exact signed APK and connected code path.

rule DIVAR_Dex_ReportDeserializer_Exact
{
  meta:
    description = "Divar ReportDeserializer class and remote-instruction schema"
    target = "DEX child; exact Divar family locator"
    confidence = "high for class family; not proof of execution"
    date = "2026-10-04"
  strings:
    $class = "Lir/divar/chat/util/ReportDeserializer;" ascii
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $local = "local" ascii
  condition:
    uint32(0) == 0x0a786564 and $class and all of ($objectify, $deserialize, $local)
}

// The next three rules classify sampled worker implementations. The exact
// register bytes are compiler-sensitive and are not a substitute for decompile.

rule DIVAR_Dex_Worker_PlainURL_Candidate
{
  meta:
    description = "Divar worker schema without either sampled XOR URL loop"
    target = "DEX child; sampled 2023 plain-URL candidate"
    confidence = "medium; absence of byte pattern is not proof of plain URL"
    date = "2026-10-04"
  strings:
    $class = "Lir/divar/chat/util/ReportDeserializer;" ascii
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $report = "report" ascii
    $local = "local" ascii
    $reflect = "getMethod" ascii
    $x63a = { DF 04 04 3F }
    $x63b = { DF 05 05 3F }
    $x104a = { DF 04 04 68 }
    $x104b = { DF 05 05 68 }
  condition:
    uint32(0) == 0x0a786564 and all of ($class, $objectify, $deserialize, $report, $local, $reflect) and
    not any of ($x*)
}

rule DIVAR_Dex_Worker_XOR63_Candidate
{
  meta:
    description = "Divar worker schema with sampled XOR 63 URL loop"
    target = "DEX child; sampled 2023-25 encoded worker candidate"
    confidence = "medium; verify decoded URL construction"
    date = "2026-10-04"
  strings:
    $class = "Lir/divar/chat/util/ReportDeserializer;" ascii
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $report = "report" ascii
    $local = "local" ascii
    $reflect = "getMethod" ascii
    $x63a = { DF 04 04 3F }
    $x63b = { DF 05 05 3F }
  condition:
    uint32(0) == 0x0a786564 and all of ($class, $objectify, $deserialize, $report, $local, $reflect) and
    any of ($x63*)
}

rule DIVAR_Dex_Worker_XOR104_Candidate
{
  meta:
    description = "Divar worker schema with sampled XOR 104 URL loop"
    target = "DEX child; sampled 2026 encoded worker candidate"
    confidence = "medium; verify decoded URL construction"
    date = "2026-10-04"
  strings:
    $class = "Lir/divar/chat/util/ReportDeserializer;" ascii
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $report = "report" ascii
    $local = "local" ascii
    $reflect = "getMethod" ascii
    $x104a = { DF 04 04 68 }
    $x104b = { DF 05 05 68 }
  condition:
    uint32(0) == 0x0a786564 and all of ($class, $objectify, $deserialize, $report, $local, $reflect) and
    any of ($x104*)
}

// These rules omit the Divar class name to triage possible cross-app reuse.
// Co-occurrence within one DEX does not establish a connected data flow.

rule ANDROID_Dex_ReflectiveStageSchema_Triage
{
  meta:
    description = "Unusual remote-instruction schema with network fetch and reflection"
    target = "DEX child; class-neutral cross-app triage including plain-URL variants"
    confidence = "medium; verify one reachable worker method"
    date = "2026-10-04"
  strings:
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii fullword
    $report = "report" ascii fullword
    $local = "local" ascii fullword
    $format = "format" ascii fullword
    $parse = "parse" ascii fullword
    $reflect = "getMethod" ascii
    $network = "openConnection" ascii
  condition:
    uint32(0) == 0x0a786564 and all of them
}

rule ANDROID_Dex_PushRelay_Opcode_Triage
{
  meta:
    description = "Push sender plus receiver Dalvik opcode sequence from sampled Divar builds"
    target = "DEX child; register-layout-sensitive triage"
    confidence = "medium; disassemble and confirm data flow"
    date = "2026-10-04"
  strings:
    $push = "push_id" ascii
    $callback = "callback_url" ascii
    $campaign = "campaign" ascii
    $action = "action" ascii
    $relay = { 6E 30 ?? ?? ?? ?? 0C ?? 71 10 ?? ?? ?? ?? 0C ?? 6E 20 ?? ?? ?? ?? 0C ?? 6E 30 ?? ?? ?? ?? 0C ?? 6E 20 ?? ?? ?? ?? }
    $recv = { 6E 20 ?? ?? ?? ?? 0C ?? 71 20 ?? ?? ?? ?? 0A ?? 38 ?? ?? ?? 22 ?? ?? ?? 22 ?? ?? ?? 70 30 ?? ?? ?? ?? 70 20 ?? ?? ?? ?? 6E 10 ?? ?? ?? ?? 0E 00 }
  condition:
    uint32(0) == 0x0a786564 and all of them
}

rule ANDROID_Dex_XOR63_Schema_Triage
{
  meta:
    description = "Exact XOR 63 opcode candidate plus Divar-like instruction schema"
    target = "DEX child; cross-app triage"
    confidence = "medium; opcode layout and schema may occur independently"
    date = "2026-10-04"
  strings:
    $xor_a = { DF 04 04 3F }
    $xor_b = { DF 05 05 3F }
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $report = "report" ascii
    $local = "local" ascii
    $reflect = "getMethod" ascii
  condition:
    uint32(0) == 0x0a786564 and ($xor_a or $xor_b) and
    all of ($objectify, $deserialize, $report, $local, $reflect)
}

rule ANDROID_Dex_XOR104_Schema_Triage
{
  meta:
    description = "Exact XOR 104 opcode candidate plus Divar-like instruction schema"
    target = "DEX child; cross-app triage"
    confidence = "medium; opcode layout and schema may occur independently"
    date = "2026-10-04"
  strings:
    $xor_a = { DF 04 04 68 }
    $xor_b = { DF 05 05 68 }
    $objectify = "objectify" ascii fullword
    $deserialize = "deserialize" ascii
    $report = "report" ascii
    $local = "local" ascii
    $reflect = "getMethod" ascii
  condition:
    uint32(0) == 0x0a786564 and ($xor_a or $xor_b) and
    all of ($objectify, $deserialize, $report, $local, $reflect)
}

rule ANDROID_Dex_HTTP_ResponseHeader_Triage
{
  meta:
    description = "X-CORRELATION-ID response-header relay to an explicit Android broadcast"
    target = "DEX child; header-branch triage"
    confidence = "medium; validate interceptor wiring and header decoding"
    date = "2026-10-04"
  strings:
    $header = "X-CORRELATION-ID" ascii
    $base64_type = "Landroid/util/Base64;" ascii
    $class = "setClassName" ascii
    $broadcast = "sendBroadcast" ascii
  condition:
    uint32(0) == 0x0a786564 and all of them
}
