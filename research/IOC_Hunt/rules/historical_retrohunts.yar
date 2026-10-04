// Exact rules used in the three 3 October 2026 VirusTotal Retrohunt jobs.
// Kept unchanged for reproducibility. The first rule is too noisy for routine use.

rule android_xor_payload_schema_triage {
 strings:
  $xor_a = { DF 05 05 68 }
  $xor_b = { DF 04 04 68 }
  $k_format = "format" ascii
  $k_parse = "parse" ascii
  $k_data = "data" ascii
  $k_report = "report" ascii
  $k_objectify = "objectify" ascii
  $k_deserialize = "deserialize" ascii
  $k_extra = "extra" ascii
  $k_local = "local" ascii
  $reflect = "getMethod" ascii
 condition:
  uint32(0)==0x0a786564 and ($xor_a or $xor_b) and $reflect and 6 of ($k_*)
}

rule android_xor_payload_schema_strict {
 strings:
  $xor_a = { DF 05 05 68 }
  $xor_b = { DF 04 04 68 }
  $objectify = "objectify" ascii
  $deserialize = "deserialize" ascii
  $report = "report" ascii
  $local = "local" ascii
  $reflect = "getMethod" ascii
 condition:
  uint32(0)==0x0a786564 and ($xor_a or $xor_b) and $reflect and all of ($objectify,$deserialize,$report,$local)
}

rule divar_push_relay_triage {
 strings:
  $a = "push_id" ascii
  $b = "callback_url" ascii
  $c = "campaign" ascii
  $d = "action" ascii
  $relay = { 6E 30 ?? ?? ?? ?? 0C ?? 71 10 ?? ?? ?? ?? 0C ?? 6E 20 ?? ?? ?? ?? 0C ?? 6E 30 ?? ?? ?? ?? 0C ?? 6E 20 ?? ?? ?? ?? }
  $recv = { 6E 20 ?? ?? ?? ?? 0C ?? 71 20 ?? ?? ?? ?? 0A ?? 38 ?? ?? ?? 22 ?? ?? ?? 22 ?? ?? ?? 70 30 ?? ?? ?? ?? 70 20 ?? ?? ?? ?? 6E 10 ?? ?? ?? ?? 0E 00 }
 condition:
  uint32(0)==0x0a786564 and all of them
}
