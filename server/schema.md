# CSV files schema

_Generated: 2026-06-07 15:27_

> Types are inferred from a sample of up to **2000 rows** per file. A column may hold different values further down (e.g. nulls or decimals not seen in the sample), so treat these as a strong hint, not a guarantee. Samsung Health files have a metadata line first; it is skipped and its type name shown below.

---

## `com.samsung.health.device_profile.20260607134546.csv`

- Data type: `com.samsung.health.device_profile`
- Total rows (approx.): **8** · Columns: **20** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 8 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| manufacturer | string | 0 | `Samsung`, `Combined`, `all_target` |
| providing_step_goal | floating | 6 | `1.0` |
| create_sh_ver | floating | 8 | _(no data)_ |
| step_source_group | floating | 6 | `15.0`, `103.0` |
| device_type | floating | 6 | `10040.0`, `10053.0` |
| backsync_step_goal | floating | 6 | `1.0` |
| capability | string | 6 | `9f01b61a-461d-c1e8-3efe-7f75b3eb1c75.cap...`, `b05eb2b5-02ad-408f-85ea-00bc3f0f21da.cap...` |
| modify_sh_ver | floating | 7 | `63200010.0` |
| device_group | integer | 0 | `360001`, `0`, `360003` |
| update_time | string | 0 | `2024-01-01 03:42:05.658`, `2022-03-24 17:06:48.034`, `2022-03-24 17:06:51.236` |
| create_time | datetime (text) | 0 | `2022-03-16 12:01:07.930`, `2022-03-24 17:06:48.034`, `2022-03-24 17:06:51.236` |
| name | string | 0 | `My Device`, `Combined`, `all_target` |
| model | string | 1 | `SM-S901E`, `Combined`, `all_target` |
| legacy_deviceuuid | floating | 8 | _(no data)_ |
| connectivity_type | floating | 8 | _(no data)_ |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `VfS0qUERdZ`, `Mk66SbFqK1` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| accessory_type | floating | 8 | _(no data)_ |
| fixed_name | string | 0 | `S22 de Santiago`, `Galaxy S8+`, `Galaxy A30` |
| datauuid | string | 0 | `1f190ad9-40f2-9f2e-f2ba-6514109f1ef9`, `7af9722c-cd99-07b7-853a-43ce58e819c5`, `471ca32b-a665-1e9e-7c27-7ac69485dc05` |

---

## `com.samsung.health.floors_climbed.20260607134546.csv`

- Data type: `com.samsung.health.floors_climbed`
- Total rows (approx.): **468** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 468 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| start_time | datetime (text) | 0 | `2020-06-28 15:26:45.000`, `2022-07-09 20:30:02.999`, `2022-07-09 21:26:23.000` |
| custom | floating | 468 | _(no data)_ |
| update_time | datetime (text) | 0 | `2020-06-28 15:28:10.832`, `2022-07-09 20:30:16.970`, `2022-07-09 21:29:07.744` |
| create_time | datetime (text) | 0 | `2020-06-28 15:28:10.820`, `2022-07-09 20:30:16.970`, `2022-07-09 21:29:07.744` |
| client_data_id | floating | 468 | _(no data)_ |
| client_data_ver | floating | 468 | _(no data)_ |
| floor | floating | 0 | `1.0`, `3.0`, `2.0` |
| raw_data | string | 313 | `3ffc5f64-1a6e-4d6e-9814-978d741b96f9.raw...`, `f1649232-6d45-4835-a4c1-957fb1707d2f.raw...`, `a47dc337-e0be-4777-bb1b-e823ec450582.raw...` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `gp5ou4ds4l`, `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | datetime (text) | 0 | `2020-06-28 15:26:56.000`, `2022-07-09 20:30:11.999`, `2022-07-09 21:26:34.000` |
| datauuid | string | 0 | `ff874fce-9779-8e25-febf-460a55650764`, `e0b503a3-985a-41a2-8f5a-7e07dd33eb95`, `2a6ce09f-c14b-4b85-974a-91ef144d3b78` |

---

## `com.samsung.health.height.20260607134546.csv`

- Data type: `com.samsung.health.height`
- Total rows (approx.): **4** · Columns: **11** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 4 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 3 | `62900750.0` |
| start_time | datetime (text) | 0 | `2020-06-22 19:49:18.967`, `2021-09-07 12:23:23.370`, `2022-07-02 22:18:53.657` |
| custom | floating | 4 | _(no data)_ |
| height | floating | 0 | `160.0`, `169.0`, `171.0` |
| modify_sh_ver | floating | 3 | `62900750.0` |
| update_time | datetime (text) | 0 | `2020-06-22 19:49:18.967`, `2021-09-07 12:23:23.370`, `2022-07-02 22:18:53.670` |
| create_time | datetime (text) | 0 | `2020-06-22 19:50:33.918`, `2021-09-07 12:27:21.896`, `2022-07-02 22:18:53.670` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `gp5ou4ds4l`, `Cv7sH/e0hQ`, `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `901d51f2-73e9-4638-9eac-a19ad6414a9f`, `7b32454a-65e5-432f-8806-5e32b9582737`, `f9deb535-17a3-441e-bd2c-789aa048d099` |

---

## `com.samsung.health.hrv.20260607134546.csv`

- Data type: `com.samsung.health.hrv`
- Total rows (approx.): **3177** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| start_time | string | 0 | `2025-01-11 06:00:00.000`, `2025-01-11 07:00:00.000`, `2025-01-11 08:00:00.000` |
| custom | floating | 2000 | _(no data)_ |
| binning_data | string | 0 | `36531204-4d7d-45aa-b503-331c59ae7dd2.bin...`, `03fbb012-45f8-47c9-92e3-b667221a28ae.bin...`, `9b6f73e3-a2f5-408a-91e2-c68aa884b318.bin...` |
| modify_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| update_time | string | 0 | `2025-01-11 07:11:32.881`, `2025-01-11 08:16:12.825`, `2025-01-11 09:17:04.865` |
| create_time | string | 0 | `2025-01-11 07:11:32.881`, `2025-01-11 08:16:12.825`, `2025-01-11 09:17:04.865` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| comment | floating | 2000 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2025-01-11 07:00:00.000`, `2025-01-11 08:00:00.000`, `2025-01-11 09:00:00.000` |
| datauuid | string | 0 | `36531204-4d7d-45aa-b503-331c59ae7dd2`, `03fbb012-45f8-47c9-92e3-b667221a28ae`, `9b6f73e3-a2f5-408a-91e2-c68aa884b318` |

---

## `com.samsung.health.movement.20260607134546.csv`

- Data type: `com.samsung.health.movement`
- Total rows (approx.): **5879** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| start_time | string | 0 | `2025-01-11 05:47:00.000`, `2025-01-11 06:00:00.000`, `2025-01-11 07:00:00.000` |
| custom | floating | 2000 | _(no data)_ |
| binning_data | string | 0 | `cd54cc97-2638-4933-a177-a2ef39b4d8b6.bin...`, `c32dafeb-2fb5-430f-ac05-dc8e40d3d664.bin...`, `fa4f177c-4b13-4fce-971b-4f223a43b5ef.bin...` |
| modify_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| update_time | string | 0 | `2025-01-11 06:07:31.926`, `2025-01-11 07:11:32.079`, `2025-01-11 08:08:40.254` |
| create_time | string | 0 | `2025-01-11 06:07:31.926`, `2025-01-11 06:07:31.951`, `2025-01-11 07:11:32.409` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| comment | floating | 2000 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2025-01-11 05:59:59.999`, `2025-01-11 06:59:59.999`, `2025-01-11 07:59:59.999` |
| datauuid | string | 0 | `cd54cc97-2638-4933-a177-a2ef39b4d8b6`, `c32dafeb-2fb5-430f-ac05-dc8e40d3d664`, `fa4f177c-4b13-4fce-971b-4f223a43b5ef` |

---

## `com.samsung.health.oxygen_saturation.raw.20260607134546.csv`

- Data type: `com.samsung.health.oxygen_saturation.raw`
- Total rows (approx.): **35** · Columns: **11** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 35 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| start_time | string | 0 | `2026-05-03 07:46:00.000`, `2026-05-04 04:32:00.000`, `2026-05-05 03:34:00.000` |
| binning_data | string | 0 | `d38e47c4-da0c-4497-9606-912048c43373.bin...`, `c9282a65-a3f3-40d9-8728-258fd9976f0d.bin...`, `14e75d73-5a76-44c4-aa5f-cc3c55b11e1b.bin...` |
| update_time | string | 0 | `2026-05-03 14:38:44.077`, `2026-05-04 09:34:32.373`, `2026-05-05 11:00:45.056` |
| create_time | string | 0 | `2026-05-03 14:38:44.077`, `2026-05-04 09:34:32.373`, `2026-05-05 11:00:45.056` |
| is_integrated | floating | 35 | _(no data)_ |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| comment | floating | 35 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2026-05-03 14:13:00.000`, `2026-05-04 09:34:00.000`, `2026-05-05 10:54:00.000` |
| datauuid | string | 0 | `d38e47c4-da0c-4497-9606-912048c43373`, `c9282a65-a3f3-40d9-8728-258fd9976f0d`, `14e75d73-5a76-44c4-aa5f-cc3c55b11e1b` |

---

## `com.samsung.health.respiratory_rate.20260607134546.csv`

- Data type: `com.samsung.health.respiratory_rate`
- Total rows (approx.): **456** · Columns: **20** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 456 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| start_time | string | 0 | `2025-01-11 06:42:00.000`, `2025-01-12 06:25:00.000`, `2025-01-15 05:35:00.000` |
| custom | floating | 456 | _(no data)_ |
| binning_data | string | 0 | `80b78c77-ba96-42fd-be10-792a7cba0d90.bin...`, `d8226e9b-ae07-431e-ac9e-d19580ece76b.bin...`, `8a21fcce-d81d-459f-9ff1-643f8be0deed.bin...` |
| modify_sh_ver | integer | 0 | `62800471`, `62900571`, `62910031` |
| average | floating | 0 | `16.029589`, `15.733309`, `15.789318` |
| lower_limit | floating | 0 | `0.0`, `15.684801`, `15.407887` |
| update_time | string | 0 | `2025-01-11 13:34:29.512`, `2025-01-12 14:02:20.121`, `2025-01-15 12:52:21.692` |
| create_time | string | 0 | `2025-01-11 13:34:29.512`, `2025-01-12 14:02:20.121`, `2025-01-15 12:52:21.692` |
| client_data_id | floating | 456 | _(no data)_ |
| upper_limit | floating | 0 | `0.0`, `16.006351`, `16.048128` |
| client_data_ver | floating | 456 | _(no data)_ |
| is_outlier | integer | 0 | `0`, `1` |
| pplib_version | datetime (text) | 0 | `1.01.04` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| comment | floating | 456 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2025-01-11 13:09:00.000`, `2025-01-12 13:36:00.000`, `2025-01-15 12:32:00.000` |
| datauuid | string | 0 | `80b78c77-ba96-42fd-be10-792a7cba0d90`, `d8226e9b-ae07-431e-ac9e-d19580ece76b`, `8a21fcce-d81d-459f-9ff1-643f8be0deed` |

---

## `com.samsung.health.sleep_stage.20260607134546.csv`

- Data type: `com.samsung.health.sleep_stage`
- Total rows (approx.): **76805** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 2000 | _(no data)_ |
| start_time | datetime (text) | 0 | `2022-07-15 03:55:00.000`, `2022-07-15 04:16:00.000`, `2022-07-15 04:32:00.000` |
| sleep_id | string | 0 | `8a7054e7-026c-492b-9b4d-119fc5e032fd`, `22b7480c-84db-42ba-a945-ffdc2f71665c`, `22ebd28c-d66f-44e2-a79b-c2d4f6e598f2` |
| custom | floating | 2000 | _(no data)_ |
| modify_sh_ver | floating | 2000 | _(no data)_ |
| update_time | datetime (text) | 0 | `2022-07-15 10:22:28.200`, `2022-07-15 10:22:28.201`, `2022-07-15 10:22:28.202` |
| create_time | datetime (text) | 0 | `2022-07-15 10:22:28.200`, `2022-07-15 10:22:28.201`, `2022-07-15 10:22:28.202` |
| stage | integer | 0 | `40002`, `40003`, `40001` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | datetime (text) | 0 | `2022-07-15 04:16:00.000`, `2022-07-15 04:32:00.000`, `2022-07-15 04:33:00.000` |
| datauuid | string | 0 | `d56a957f-aa99-46f7-807c-27d64ba6ca9b`, `1143c802-950e-437c-a406-914878c3814a`, `34ea97c2-5631-4a59-ab4a-2fc3178fd266` |

---

## `com.samsung.health.user_profile.20260607134546.csv`

- Data type: `com.samsung.health.user_profile`
- Total rows (approx.): **22** · Columns: **14** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 22 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| text_value | string | 6 | `20060701`, `COL`, `kg` |
| create_sh_ver | floating | 19 | `62660010.0`, `62900750.0` |
| float_value | floating | 20 | `175.0`, `54.0` |
| modify_sh_ver | floating | 14 | `62900750.0`, `63051050.0`, `63110130.0` |
| update_time | string | 0 | `2025-02-07 13:28:54.246`, `2022-03-16 12:01:13.316`, `2021-09-07 12:23:28.678` |
| create_time | datetime (text) | 0 | `2022-03-16 12:01:13.318`, `2022-03-16 12:01:13.320`, `2021-09-07 12:14:42.980` |
| long_value | floating | 22 | _(no data)_ |
| key | string | 0 | `birth_date`, `country`, `weight_unit` |
| blob_value | string | 20 | `00000000-0000-0000-0000-000000000016.das...`, `00000000-0000-0000-0000-000000000002.ima...` |
| int_value | floating | 21 | `180005.0` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `gp5ou4ds4l`, `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| double_value | floating | 22 | _(no data)_ |
| datauuid | string | 0 | `00000000-0000-0000-0000-00000000000a`, `00000000-0000-0000-0000-000000000001`, `00000000-0000-0000-0000-000000000007` |

---

## `com.samsung.health.weight.20260607134546.csv`

- Data type: `com.samsung.health.weight`
- Total rows (approx.): **66** · Columns: **25** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 66 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| body_fat_mass | floating | 3 | `3.7308254`, `6.684122`, `6.8061132` |
| create_sh_ver | floating | 50 | `62600630.0`, `62620030.0`, `62660011.0` |
| start_time | datetime (text) | 0 | `2020-06-22 19:49:25.780`, `2021-09-07 12:23:28.669`, `2022-07-02 22:18:53.642` |
| custom | floating | 66 | _(no data)_ |
| height | floating | 2 | `171.0`, `169.0`, `175.0` |
| weight | floating | 0 | `38.0`, `50.0`, `49.4` |
| muscle_mass | floating | 66 | _(no data)_ |
| modify_sh_ver | floating | 50 | `62600630.0`, `62620030.0`, `62660011.0` |
| update_time | datetime (text) | 0 | `2020-06-22 19:49:25.780`, `2021-09-07 12:23:28.669`, `2022-07-02 22:18:53.671` |
| create_time | datetime (text) | 0 | `2020-06-22 19:50:34.155`, `2021-09-07 12:27:22.056`, `2022-07-02 22:18:53.671` |
| client_data_id | floating | 66 | _(no data)_ |
| skeletal_muscle | floating | 3 | `50.409435`, `46.597576`, `46.43377` |
| fat_free_mass | floating | 3 | `46.269173`, `43.31588`, `43.193886` |
| client_data_ver | floating | 66 | _(no data)_ |
| basal_metabolic_rate | floating | 3 | `1369.0`, `1305.0`, `1302.0` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `gp5ou4ds4l`, `Cv7sH/e0hQ`, `1kGlEKqwGK` |
| skeletal_muscle_mass | floating | 3 | `25.20472`, `23.298788`, `23.216885` |
| comment | floating | 66 | _(no data)_ |
| fat_free | floating | 3 | `92.538345`, `86.63176`, `86.38777` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| body_fat | floating | 3 | `7.461651`, `13.368244`, `13.612227` |
| datauuid | string | 0 | `6c1e8e42-89e3-4a36-9e3d-1091bb0fbd15`, `cba13972-0eee-463f-b3ca-e97114d08f6f`, `38ed29d7-a815-43e7-9d3c-891e1cbb6e57` |
| vfa_level | floating | 66 | _(no data)_ |
| total_body_water | floating | 3 | `33.895824`, `31.715878`, `31.625278` |

---

## `com.samsung.shealth.activity.day_summary.20260607134546.csv`

- Data type: `com.samsung.shealth.activity.day_summary`
- Total rows (approx.): **2224** · Columns: **33** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| movement_type | floating | 1302 | `0.0` |
| create_sh_ver | floating | 1330 | `62600630.0`, `62610110.0`, `62620030.0` |
| energy_type | floating | 1302 | `0.0` |
| exercise_time | floating | 1302 | `3205192.0`, `0.0`, `3186755.0` |
| step_count | integer | 0 | `673`, `0`, `1813` |
| exercise_calorie_target | floating | 1302 | `300.0` |
| active_time | integer | 0 | `442828`, `0`, `1140360` |
| target | floating | 455 | `90.0` |
| others_time | integer | 0 | `0`, `879705`, `845750` |
| modify_sh_ver | floating | 1302 | `62600630.0`, `62610110.0`, `62620030.0` |
| update_time | datetime (text) | 0 | `2022-03-25 04:24:55.508`, `2022-03-24 17:06:51.261`, `2022-03-24 17:07:22.660` |
| floors_target | floating | 1302 | `10.0` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:51.242`, `2022-03-24 17:06:51.261`, `2022-03-24 17:06:51.274` |
| floor_count | floating | 1302 | `0.0`, `3.0`, `4.0` |
| dynamic_active_time_target | floating | 1302 | `30.0` |
| exercise_time_target | floating | 1302 | `30.0` |
| goal | integer | 0 | `-1`, `60` |
| longest_active_time | integer | 0 | `60000`, `0`, `240000` |
| score | integer | 0 | `7`, `0`, `21` |
| move_hourly_count | floating | 1302 | `6.0`, `10.0`, `11.0` |
| duration_type | floating | 1302 | `0.0` |
| move_hourly_target | floating | 1302 | `8.0` |
| distance | floating | 0 | `494.51007`, `0.0`, `1375.49` |
| dynamic_active_time | floating | 1302 | `662000.0`, `0.0`, `1704000.0` |
| calorie | floating | 0 | `19.61`, `0.0`, `52.430004` |
| extra_data | string | 0 | `49bd8a8e-7e37-4a33-a98f-634e6a9d3a10.ext...`, `af8257f1-993b-448e-9d2a-323b4183d763.ext...`, `194472bf-85dd-489f-9fec-2af4abf199fd.ext...` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `J5dfK60+5D`, `UUqPkhoTUZ` |
| run_time | integer | 0 | `0`, `5600`, `72481` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| walk_time | integer | 0 | `442828`, `0`, `1140360` |
| longest_idle_time | integer | 0 | `56340000`, `-1`, `65040000` |
| datauuid | string | 0 | `49bd8a8e-7e37-4a33-a98f-634e6a9d3a10`, `af8257f1-993b-448e-9d2a-323b4183d763`, `194472bf-85dd-489f-9fec-2af4abf199fd` |
| day_time | datetime (text) | 0 | `2022-03-24 00:00:00.000`, `2022-02-25 00:00:00.000`, `2022-02-26 00:00:00.000` |

---

## `com.samsung.shealth.activity.goal.20260607134546.csv`

- Data type: `com.samsung.shealth.activity.goal`
- Total rows (approx.): **2** · Columns: **8** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2020-03-14 02:49:55.101`, `2019-05-31 03:34:42.595` |
| create_time | datetime (text) | 0 | `2020-03-14 02:49:55.101`, `2019-05-31 03:34:42.595` |
| value | integer | 0 | `60` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `J5dfK60+5D` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| set_time | integer | 0 | `1584154195091`, `1559273682547` |
| datauuid | string | 0 | `93f9046b-640c-4b2c-8a22-fd374a13375a`, `de5ccb65-d58b-418d-9f0e-e8ae98f520c2` |

---

## `com.samsung.shealth.activity_level.20260607134546.csv`

- Data type: `com.samsung.shealth.activity_level`
- Total rows (approx.): **5** · Columns: **8** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 5 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| activity_level | integer | 0 | `180004`, `180003`, `180005` |
| start_time | datetime (text) | 0 | `2025-01-30 11:56:06.858`, `2025-02-04 22:41:35.237`, `2025-02-20 11:45:14.348` |
| update_time | datetime (text) | 0 | `2025-01-30 11:56:06.858`, `2025-02-04 22:41:35.237`, `2025-02-20 11:45:14.348` |
| create_time | datetime (text) | 0 | `2025-01-30 11:56:06.870`, `2025-02-04 22:41:35.245`, `2025-02-20 11:45:14.368` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `12b58e45-526b-462a-a019-2f01d8e55efd`, `f77b776d-167d-46ed-895f-f597f3eba212`, `c2601d04-a131-458e-bd86-09b83dfe54d8` |

---

## `com.samsung.shealth.alerted_stress.20260607134546.csv`

- Data type: `com.samsung.shealth.alerted_stress`
- Total rows (approx.): **44** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 44 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `63070031`, `63110011`, `63200011` |
| start_time | string | 0 | `2026-02-10 13:49:39.017`, `2026-03-26 02:43:34.018`, `2026-03-26 03:09:48.014` |
| modify_sh_ver | integer | 0 | `63070031`, `63110011`, `63200011` |
| update_time | string | 0 | `2026-02-10 13:49:39.158`, `2026-03-26 02:46:35.112`, `2026-03-26 03:09:48.294` |
| create_time | string | 0 | `2026-02-10 13:49:39.158`, `2026-03-26 02:46:35.112`, `2026-03-26 03:09:48.294` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2026-02-10 13:49:39.017`, `2026-03-26 02:43:34.018`, `2026-03-26 03:09:48.014` |
| datauuid | string | 0 | `b7abf0df-8d7f-4823-bdbd-b48c22aaeb74`, `a53f0e9f-9d83-4a8b-a11b-49cb91bfa211`, `26d2a335-e7ab-4073-ac8a-ed6181abf5c7` |

---

## `com.samsung.shealth.badge.20260607134546.csv`

- Data type: `com.samsung.shealth.badge`
- Total rows (approx.): **221** · Columns: **20** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 221 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| number_of_streak | floating | 73 | `1.0`, `0.0`, `4.0` |
| start_time | datetime (text) | 0 | `2023-07-26 00:10:52.197`, `2023-07-27 05:00:00.000`, `2023-10-18 22:24:06.170` |
| exercise_type | floating | 208 | `10007.0`, `14001.0`, `15005.0` |
| device_type | floating | 220 | `100003.0` |
| status | integer | 0 | `1`, `0`, `2` |
| sleep_coaching_session_uuid | string | 220 | `275c008c-bb3b-4e5a-ada2-c36f825e0c50` |
| update_time | datetime (text) | 0 | `2023-07-26 05:10:52.249`, `2023-07-27 21:11:04.080`, `2023-10-18 23:09:10.035` |
| create_time | datetime (text) | 0 | `2023-07-26 05:10:52.249`, `2023-07-27 21:11:04.080`, `2023-10-18 23:09:10.035` |
| source_pkg_name | string | 220 | `com.sec.android.app.shealth` |
| key | string | 0 | `sleep_goal_first_sleep`, `step_milestone_10k_steps`, `exercise_goal_first_achieve` |
| program_id | floating | 221 | _(no data)_ |
| is_shown | floating | 220 | `1.0` |
| time_offset | string | 0 | `UTC+0000`, `UTC-0500` |
| extra_data | string | 218 | `7496.99969959259`, `1777265999999,1`, `{"a":false}` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| exercise_data_uuid | string | 205 | `f5f2f57f-3cb0-499b-bcab-ecd70bb64499`, `ee166a50-5a1e-428b-a59c-358fed12a977`, `d0ae9baf-3ab4-4426-ae61-7513c6330059` |
| controller_id | string | 0 | `Sleep.Goal`, `tracker.pedometer`, `tracker.exercise` |
| end_time | datetime (text) | 0 | `2023-07-26 00:10:52.197`, `2023-07-27 05:00:00.000`, `2023-10-18 23:09:07.890` |
| datauuid | string | 0 | `e860b55c-8e2e-48e6-9048-d89f9b7eba97`, `eff137a4-4102-4d4b-bec8-62bd53b6a3f0`, `7f2e9d2b-4c67-4a10-9e09-b91d94730fd2` |

---

## `com.samsung.shealth.best_records.20260607134546.csv`

- Data type: `com.samsung.shealth.best_records`
- Total rows (approx.): **35** · Columns: **15** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 35 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| source_id | string | 7 | `766d3135-eea4-4dd4-ae55-b1594c2d7d04`, `5c13d72f-ca89-4a59-876f-5bd52802ae4c`, `af414c5e-dcb7-4598-8e34-c81651a29122` |
| device_type | floating | 12 | `-1.0`, `-100003.0` |
| update_time | datetime (text) | 0 | `2023-06-22 11:52:52.347`, `2023-06-22 11:52:52.345`, `2023-06-22 11:52:52.356` |
| create_time | datetime (text) | 0 | `2022-03-26 11:47:09.516`, `2022-03-26 11:47:09.547`, `2022-07-04 14:20:02.236` |
| source_pkg_name | floating | 35 | _(no data)_ |
| date | integer | 0 | `1648274983445`, `1656925630938`, `1657475910658` |
| type | integer | 0 | `1`, `2`, `4` |
| value | floating | 0 | `1502026.0`, `94.0`, `101.39` |
| is_shown | floating | 32 | `1.0`, `0.0` |
| extra_data | floating | 35 | _(no data)_ |
| extra_type | floating | 12 | `10007.0`, `-1.0`, `15005.0` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `Cv7sH/e0hQ`, `VfS0qUERdZ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| controller_id | string | 0 | `tracker.sport_others`, `tracker.sport_walking`, `tracker.sport_running` |
| datauuid | string | 0 | `b9b4951c-02b3-4fe7-8520-c9c469a67973`, `13d10f29-1215-46ff-bcea-ec992b9f7754`, `9a0ab50f-bea3-4ce8-8de5-f819d3984867` |

---

## `com.samsung.shealth.breathing.20260607134546.csv`

- Data type: `com.samsung.shealth.breathing`
- Total rows (approx.): **3** · Columns: **18** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| duration | integer | 0 | `60`, `300` |
| create_sh_ver | floating | 3 | _(no data)_ |
| start_time | string | 0 | `2022-07-02 22:22:22.029`, `2022-07-18 18:37:53.291`, `2025-07-02 05:26:42.468` |
| exhale_hold_duration | floating | 3 | _(no data)_ |
| custom | floating | 3 | _(no data)_ |
| modify_sh_ver | floating | 3 | _(no data)_ |
| update_time | string | 0 | `2022-07-02 22:22:22.031`, `2022-07-18 18:37:53.295`, `2025-07-02 05:26:42.484` |
| create_time | string | 0 | `2022-07-02 22:22:22.031`, `2022-07-18 18:37:53.295`, `2025-07-02 05:26:42.484` |
| exhale_duration | floating | 3 | _(no data)_ |
| type | floating | 3 | _(no data)_ |
| cycle | integer | 0 | `6`, `30` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| inhale_hold_duration | floating | 3 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2022-07-02 22:22:22.029`, `2022-07-18 18:37:53.291`, `2025-07-02 05:26:42.468` |
| datauuid | string | 0 | `7e68002c-0f03-4807-b88a-e7de08622689`, `7dd695b2-933a-40da-9f6e-c811a5b64ac4`, `83eb9ad3-0771-4ee2-8a84-6b357666af1e` |
| inhale_duration | floating | 3 | _(no data)_ |

---

## `com.samsung.shealth.calories_burned.details.20260607134546.csv`

- Data type: `com.samsung.shealth.calories_burned.details`
- Total rows (approx.): **2218** · Columns: **17** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| active_calories_goal | floating | 2000 | _(no data)_ |
| version | floating | 2000 | _(no data)_ |
| extra_data | string | 0 | `4158ea0e-4aa5-4393-bb5e-5ea3d7d3e2bb.ext...`, `9079d197-a87d-4228-8021-22882d834f41.ext...`, `0335c61e-0989-494a-ab91-7170d214d965.ext...` |
| exercise_calories | floating | 2000 | _(no data)_ |
| total_exercise_calories | floating | 1302 | `355.35004`, `0.0`, `402.99002` |
| com.samsung.shealth.calories_burned.create_sh_ver | floating | 1330 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.shealth.calories_burned.tef_calorie | floating | 0 | `0.0` |
| com.samsung.shealth.calories_burned.active_time | integer | 0 | `442828`, `930669`, `0` |
| com.samsung.shealth.calories_burned.rest_calorie | floating | 0 | `1442.594`, `1434.4067`, `1450.0259` |
| com.samsung.shealth.calories_burned.modify_sh_ver | floating | 1302 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.shealth.calories_burned.update_time | datetime (text) | 0 | `2022-03-25 05:00:02.548`, `2022-03-24 17:07:23.399`, `2022-03-24 17:07:23.405` |
| com.samsung.shealth.calories_burned.create_time | datetime (text) | 0 | `2022-03-24 17:06:51.253`, `2022-03-24 17:06:51.679`, `2022-03-24 17:06:51.693` |
| com.samsung.shealth.calories_burned.active_calorie | floating | 0 | `19.61`, `61.820004`, `0.0` |
| com.samsung.shealth.calories_burned.deviceuuid | string | 0 | `1kGlEKqwGK`, `J5dfK60+5D`, `UUqPkhoTUZ` |
| com.samsung.shealth.calories_burned.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.shealth.calories_burned.datauuid | string | 0 | `4158ea0e-4aa5-4393-bb5e-5ea3d7d3e2bb`, `9079d197-a87d-4228-8021-22882d834f41`, `0335c61e-0989-494a-ab91-7170d214d965` |
| com.samsung.shealth.calories_burned.day_time | integer | 0 | `1648080000000`, `1645920000000`, `1646006400000` |

---

## `com.samsung.shealth.exercise.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise`
- Total rows (approx.): **1329** · Columns: **73** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1329 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| live_data_internal | string | 152 | `766d3135-eea4-4dd4-ae55-b1594c2d7d04.liv...`, `95dc933a-b31f-4ccf-b771-ef075fc28e32.liv...`, `e8212579-6a0f-49d1-b5f0-8b4bbf42fc4a.liv...` |
| mission_value | floating | 1313 | `0.0` |
| race_target | floating | 723 | `0.0` |
| subset_data | floating | 1329 | _(no data)_ |
| start_longitude | floating | 1328 | `-74.13187` |
| routine_datauuid | floating | 1329 | _(no data)_ |
| total_calorie | floating | 150 | `43.08`, `62.83`, `40.22` |
| completion_status | floating | 1167 | `1.0`, `0.0` |
| pace_info_id | floating | 1329 | _(no data)_ |
| activity_type | floating | 1326 | `0.0` |
| pace_live_data | floating | 1329 | _(no data)_ |
| sensing_status | string | 159 | `294efc60-a307-41d7-a70b-652af6ff0d1a.sen...`, `5c13d72f-ca89-4a59-876f-5bd52802ae4c.sen...`, `8b0a7b68-8552-4a29-ac23-7c6b2a58bc0c.sen...` |
| source_type | integer | 0 | `4`, `2`, `1` |
| mission_type | floating | 1167 | `0.0` |
| ftp | floating | 1329 | _(no data)_ |
| tracking_status | floating | 1170 | `0.0` |
| program_id | string | 1316 | `186317fc-f87e-46f4-89c2-ff847025f870`, `df0c2553-6feb-4d7c-9b13-63cae9abc8de`, `bbe84f32-2934-4f02-a739-afaaf5dbc475` |
| title | floating | 1329 | _(no data)_ |
| reward_status | floating | 1266 | `0.0`, `1.0`, `3.0` |
| heart_rate_sample_count | floating | 803 | `0.0`, `419.0`, `79.0` |
| start_latitude | floating | 1328 | `4.723378` |
| mission_extra_value | floating | 1313 | `0.0` |
| program_schedule_id | string | 1317 | `88f81396-0d0f-476a-84a4-d4683ee6d8ee`, `0a276855-f0f0-4632-85ae-e568bbc2e0ba`, `f7c6b786-6414-4bef-9a76-b5d1de7009e7` |
| heart_rate_deviceuuid | string | 1326 | `Cv7sH/e0hQ` |
| location_data_internal | string | 994 | `2774d25a-96e2-41f1-85c0-5994b951360d.loc...`, `af414c5e-dcb7-4598-8e34-c81651a29122.loc...`, `352abdf7-d8e4-40ce-9530-1869e839bdfc.loc...` |
| custom_id | floating | 1329 | _(no data)_ |
| additional_internal | string | 1328 | `352abdf7-d8e4-40ce-9530-1869e839bdfc.add...` |
| com.samsung.health.exercise.duration | integer | 0 | `2909692`, `3985655`, `2699763` |
| com.samsung.health.exercise.additional | string | 1306 | `ace4b05c-129c-6ca3-4f1b-eca96a44f956.com...`, `d0fc9c02-5bb8-022b-fbdf-98bb0439ab20.com...`, `90db25b6-7dfa-011a-0eee-dc60385578f1.com...` |
| com.samsung.health.exercise.create_sh_ver | floating | 621 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.exercise.mean_caloricburn_rate | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.location_data | string | 991 | `ace4b05c-129c-6ca3-4f1b-eca96a44f956.com...`, `d0fc9c02-5bb8-022b-fbdf-98bb0439ab20.com...`, `90db25b6-7dfa-011a-0eee-dc60385578f1.com...` |
| com.samsung.health.exercise.start_time | string | 0 | `2019-11-03 13:36:00.000`, `2019-08-18 21:10:03.000`, `2019-11-03 12:51:00.000` |
| com.samsung.health.exercise.exercise_type | integer | 0 | `1001`, `0`, `1002` |
| com.samsung.health.exercise.custom | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.max_altitude | floating | 1320 | `2596.022`, `2578.265`, `2720.565` |
| com.samsung.health.exercise.incline_distance | floating | 1322 | `10.111`, `131.367`, `62.876` |
| com.samsung.health.exercise.mean_heart_rate | floating | 156 | `0.0`, `151.0`, `120.0` |
| com.samsung.health.exercise.count_type | floating | 674 | `30001.0`, `30002.0` |
| com.samsung.health.exercise.mean_rpm | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.min_altitude | floating | 1320 | `2592.155`, `2573.921`, `2718.111` |
| com.samsung.health.exercise.modify_sh_ver | floating | 621 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.exercise.max_heart_rate | floating | 156 | `0.0`, `175.0`, `147.0` |
| com.samsung.health.exercise.update_time | string | 0 | `2019-11-03 14:34:08.011`, `2019-08-18 22:17:37.659`, `2019-11-03 13:44:00.538` |
| com.samsung.health.exercise.create_time | string | 0 | `2019-11-03 14:34:08.011`, `2019-08-18 22:17:37.659`, `2019-11-03 13:44:00.538` |
| com.samsung.health.exercise.client_data_id | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.max_power | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.max_speed | floating | 671 | `3.1827567`, `3.621328`, `3.6861029` |
| com.samsung.health.exercise.mean_cadence | floating | 815 | `0.0`, `88.283615`, `92.519936` |
| com.samsung.health.exercise.min_heart_rate | floating | 157 | `0.0`, `104.0`, `90.0` |
| com.samsung.health.exercise.client_data_ver | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.count | floating | 670 | `3660.0`, `1552.0`, `2521.0` |
| com.samsung.health.exercise.distance | floating | 540 | `3962.6777`, `6025.87`, `3698.0757` |
| com.samsung.health.exercise.max_caloricburn_rate | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.calorie | floating | 0 | `172.82852`, `261.10767`, `164.34721` |
| com.samsung.health.exercise.max_cadence | floating | 815 | `0.0`, `131.0`, `112.0` |
| com.samsung.health.exercise.decline_distance | floating | 1323 | `2.057`, `99.937`, `32.058` |
| com.samsung.health.exercise.vo2_max | floating | 1327 | `46.56`, `46.41` |
| com.samsung.health.exercise.time_offset | string | 0 | `UTC-0500`, `UTC-0400` |
| com.samsung.health.exercise.deviceuuid | string | 0 | `J5dfK60+5D`, `gp5ou4ds4l`, `UUqPkhoTUZ` |
| com.samsung.health.exercise.max_rpm | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.comment | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.live_data | string | 3 | `e0759f75-5862-49e7-9a99-0cc3d6b47687.com...`, `040ec9cf-4bbe-4171-a801-5563ba0a6e1b.com...`, `11980794-7d26-4ef0-88dc-f01f07f4292a.com...` |
| com.samsung.health.exercise.mean_power | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.mean_speed | floating | 553 | `1.3618891`, `1.5118895`, `1.3697779` |
| com.samsung.health.exercise.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.health.exercise.altitude_gain | floating | 1328 | `0.0` |
| com.samsung.health.exercise.altitude_loss | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.exercise_custom_type | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.auxiliary_devices | floating | 1329 | _(no data)_ |
| com.samsung.health.exercise.end_time | string | 0 | `2019-11-03 14:24:29.000`, `2019-08-18 22:16:28.000`, `2019-11-03 13:36:00.000` |
| com.samsung.health.exercise.datauuid | string | 0 | `e0759f75-5862-49e7-9a99-0cc3d6b47687`, `040ec9cf-4bbe-4171-a801-5563ba0a6e1b`, `11980794-7d26-4ef0-88dc-f01f07f4292a` |
| com.samsung.health.exercise.sweat_loss | floating | 1328 | `161.0` |

---

## `com.samsung.shealth.exercise.extension.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.extension`
- Total rows (approx.): **1** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| live_data_internal | floating | 1 | _(no data)_ |
| location_data | floating | 1 | _(no data)_ |
| update_time | datetime (text) | 0 | `2026-06-07 16:45:55.189` |
| create_time | datetime (text) | 0 | `2026-06-07 16:45:55.189` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| exercise_id | string | 0 | `82785bef-ddb0-4dbc-b0dd-655834f56637` |
| live_data | floating | 1 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| location_data_internal | floating | 1 | _(no data)_ |
| datauuid | string | 0 | `9f3b76fa-0a04-4b50-ac2a-3a6dcf829b1d` |

---

## `com.samsung.shealth.exercise.max_heart_rate.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.max_heart_rate`
- Total rows (approx.): **1** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| at_heart_rate | integer | 0 | `0` |
| start_time | datetime (text) | 0 | `2024-04-13 15:12:29.750` |
| max_heart_rate | integer | 0 | `197` |
| update_time | datetime (text) | 0 | `2024-04-13 15:12:34.854` |
| create_time | datetime (text) | 0 | `2024-04-13 15:12:34.854` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| ant_heart_rate | integer | 0 | `0` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `0a1b6a6c-5b89-42c9-a4f1-0162be48e068` |

---

## `com.samsung.shealth.exercise.periodization_training_program.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.periodization_training_program`
- Total rows (approx.): **1** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `63020270` |
| start_time | datetime (text) | 0 | `2025-07-03 04:07:29.986` |
| modify_sh_ver | integer | 0 | `63051050` |
| update_time | datetime (text) | 0 | `2025-11-06 11:02:23.412` |
| create_time | datetime (text) | 0 | `2025-07-03 04:07:30.068` |
| program | string | 0 | `1d15ab07-74db-418f-b9e1-60c79b276e9a.pro...` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `1d15ab07-74db-418f-b9e1-60c79b276e9a` |

---

## `com.samsung.shealth.exercise.periodization_training_schedule.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.periodization_training_schedule`
- Total rows (approx.): **1** · Columns: **14** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `63020270` |
| start_time | datetime (text) | 0 | `2025-07-03 04:07:29.986` |
| coach_id | string | 0 | `mcmv70zm_2v8` |
| status | integer | 0 | `1` |
| schedule | string | 0 | `f87305fd-fea5-4ed5-a56b-d44d4f360fe8.sch...` |
| modify_sh_ver | integer | 0 | `63051050` |
| update_time | datetime (text) | 0 | `2025-11-06 10:57:08.125` |
| create_time | datetime (text) | 0 | `2025-07-03 04:07:30.144` |
| type | integer | 0 | `1` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| program_uuid | string | 0 | `1d15ab07-74db-418f-b9e1-60c79b276e9a` |
| datauuid | string | 0 | `f87305fd-fea5-4ed5-a56b-d44d4f360fe8` |

---

## `com.samsung.shealth.exercise.program.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.program`
- Total rows (approx.): **13** · Columns: **16** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 13 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| duration | floating | 13 | _(no data)_ |
| planned_end_time | datetime (text) | 0 | `2022-03-28 09:00:00.000`, `2022-03-30 09:00:00.000`, `2022-04-02 09:00:00.000` |
| start_time | datetime (text) | 0 | `2022-03-24 09:00:00.000`, `2022-03-26 09:00:00.000`, `2022-03-27 09:00:00.000` |
| custom | floating | 13 | _(no data)_ |
| completion_status | integer | 0 | `200`, `100`, `300` |
| update_time | datetime (text) | 0 | `2022-03-24 17:10:35.267`, `2022-03-25 03:20:26.550`, `2022-03-25 03:21:11.486` |
| create_time | datetime (text) | 0 | `2022-03-24 17:10:35.267`, `2022-03-25 03:20:26.550`, `2022-03-25 03:21:11.486` |
| distance | floating | 13 | _(no data)_ |
| schedule_count | integer | 0 | `5`, `8` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | datetime (text) | 0 | `2022-03-28 09:00:00.000`, `2022-03-30 09:00:00.000`, `2022-04-02 09:00:00.000` |
| datauuid | string | 0 | `3784e8e7-a595-42b6-9876-650e816f2b43`, `bec8b744-2615-4355-a9b2-e5a4ed413abc`, `8cbfa287-f1a7-4009-989e-fd30b00460af` |
| info_id | string | 0 | `program.prod20`, `program.prod22`, `program.prod17` |
| is_visible | integer | 0 | `1` |

---

## `com.samsung.shealth.exercise.program_schedule.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.program_schedule`
- Total rows (approx.): **45** · Columns: **19** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 45 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| duration | integer | 0 | `0` |
| planned_date | datetime (text) | 0 | `2022-03-24 09:00:00.000`, `2022-03-25 09:00:00.000`, `2022-03-26 09:00:00.000` |
| state_update_time | datetime (text) | 0 | `2022-03-24 17:10:35.243`, `2022-03-24 17:10:35.244`, `2022-03-26 11:09:43.481` |
| week_info_id | floating | 45 | _(no data)_ |
| custom | string | 0 | `aa06b26c-ef84-4b38-b672-1b5b3dec7436.cus...`, `1855c52a-8701-4731-8cfd-ba4fb3819033.cus...`, `d595c9d9-5e4b-4870-ba44-139df7f4af57.cus...` |
| pace_info_id | integer | 0 | `0` |
| day_info_id | floating | 45 | _(no data)_ |
| update_time | datetime (text) | 0 | `2022-03-24 17:10:35.299`, `2022-03-24 17:10:35.301`, `2022-03-26 11:47:09.652` |
| create_time | datetime (text) | 0 | `2022-03-24 17:10:35.299`, `2022-03-24 17:10:35.301`, `2022-03-25 03:27:26.770` |
| state_updated_by | integer | 0 | `200` |
| program_id | string | 0 | `3784e8e7-a595-42b6-9876-650e816f2b43`, `186317fc-f87e-46f4-89c2-ff847025f870`, `df0c2553-6feb-4d7c-9b13-63cae9abc8de` |
| state | integer | 0 | `0`, `300`, `500` |
| distance | floating | 0 | `0.0` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| tracker_id | string | 35 | `766d3135-eea4-4dd4-ae55-b1594c2d7d04`, `95dc933a-b31f-4ccf-b771-ef075fc28e32|e82...`, `6a65e559-28dc-474b-8a6d-059615fd30be` |
| workout_day | integer | 0 | `1`, `0` |
| program_info_id | string | 0 | `program.prod20`, `program.prod28`, `program.prod11` |
| datauuid | string | 0 | `aa06b26c-ef84-4b38-b672-1b5b3dec7436`, `1855c52a-8701-4731-8cfd-ba4fb3819033`, `d595c9d9-5e4b-4870-ba44-139df7f4af57` |

---

## `com.samsung.shealth.exercise.program_summary.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.program_summary`
- Total rows (approx.): **8** · Columns: **20** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 8 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| start_time | datetime (text) | 0 | `2022-03-26 09:00:00.000`, `2022-05-02 09:00:00.000`, `2022-05-01 09:00:00.000` |
| custom | string | 0 | `3a5befb2-870a-4afd-9e46-f0b6f3dcb12a.cus...`, `ea9530c9-fae2-444a-82df-b7caab6a902f.cus...`, `4ab99dca-9155-476f-b85a-24ac98745da2.cus...` |
| missed_workouts | integer | 0 | `2`, `1` |
| completion_status | integer | 0 | `30` |
| total_workouts | integer | 0 | `3` |
| total_distance | floating | 0 | `0.0` |
| update_time | string | 0 | `2022-04-10 03:47:40.711`, `2022-05-02 10:09:37.602`, `2022-05-20 13:16:38.251` |
| create_time | string | 0 | `2022-04-10 03:47:40.711`, `2022-05-02 10:09:37.602`, `2022-05-20 13:16:38.251` |
| max_speed | floating | 0 | `0.0` |
| program_id | string | 0 | `186317fc-f87e-46f4-89c2-ff847025f870`, `bbe84f32-2934-4f02-a739-afaaf5dbc475`, `569945ba-52b3-46d7-bbe0-a76d84e7127d` |
| completion_percentage | integer | 0 | `33`, `0` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| total_duration | integer | 0 | `1502`, `0`, `630` |
| end_time | datetime (text) | 0 | `2022-03-30 09:00:00.000`, `2022-05-06 09:00:00.000`, `2022-05-05 09:00:00.000` |
| program_info_id | string | 0 | `program.prod28`, `program.prod11`, `program.prod27` |
| datauuid | string | 0 | `3a5befb2-870a-4afd-9e46-f0b6f3dcb12a`, `ea9530c9-fae2-444a-82df-b7caab6a902f`, `4ab99dca-9155-476f-b85a-24ac98745da2` |
| completed_workouts | integer | 0 | `1`, `0` |
| incomplete_workouts | integer | 0 | `0`, `1`, `2` |

---

## `com.samsung.shealth.exercise.recovery_heart_rate.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.recovery_heart_rate`
- Total rows (approx.): **595** · Columns: **12** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 595 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 74 | `62600630.0`, `62610110.0`, `62620030.0` |
| start_time | string | 0 | `2022-07-04 14:19:52.655`, `2022-07-07 21:56:16.487`, `2022-07-10 23:18:18.962` |
| modify_sh_ver | floating | 74 | `62600630.0`, `62610110.0`, `62620030.0` |
| update_time | string | 0 | `2022-07-04 14:21:52.784`, `2022-07-07 21:58:17.237`, `2022-07-10 23:20:19.313` |
| create_time | string | 0 | `2022-07-04 14:21:52.784`, `2022-07-07 21:58:17.237`, `2022-07-10 23:20:19.313` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| exercise_id | string | 0 | `5c13d72f-ca89-4a59-876f-5bd52802ae4c`, `8b0a7b68-8552-4a29-ac23-7c6b2a58bc0c`, `af414c5e-dcb7-4598-8e34-c81651a29122` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2022-07-04 14:21:52.655`, `2022-07-07 21:58:16.487`, `2022-07-10 23:20:18.962` |
| datauuid | string | 0 | `c67a6f73-370c-460e-9bfd-bbcd5d417c7f`, `a701288d-88d2-46aa-b091-b20e85f89742`, `fc4f79ff-2443-4963-8c73-cdf81dde3bfd` |
| heart_rate | string | 0 | `c67a6f73-370c-460e-9bfd-bbcd5d417c7f.hea...`, `a701288d-88d2-46aa-b091-b20e85f89742.hea...`, `fc4f79ff-2443-4963-8c73-cdf81dde3bfd.hea...` |

---

## `com.samsung.shealth.exercise.weather.20260607134546.csv`

- Data type: `com.samsung.shealth.exercise.weather`
- Total rows (approx.): **2** · Columns: **25** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| uv_index | floating | 2 | _(no data)_ |
| sunset_time | floating | 2 | _(no data)_ |
| start_time | string | 0 | `2022-07-10 23:11:50.248`, `2025-01-17 13:32:18.012` |
| latitude | floating | 0 | `4.8133364`, `4.723378` |
| custom | floating | 2 | _(no data)_ |
| wind_direction | string | 0 | `40.NE`, `30.NNE` |
| phrase | string | 0 | `Parcialmente nublado`, `Fair` |
| sundown_time | floating | 2 | _(no data)_ |
| temperature_scale | integer | 0 | `1` |
| content_provider | string | 0 | `TWC` |
| update_time | string | 0 | `2022-07-10 23:18:19.553`, `2025-01-17 13:47:00.389` |
| create_time | string | 0 | `2022-07-10 23:18:19.553`, `2025-01-17 13:47:00.389` |
| type | integer | 0 | `1` |
| longitude | floating | 0 | `-74.09902`, `-74.13187` |
| temperature | floating | 0 | `20.0`, `13.0` |
| humidity | integer | 0 | `65`, `79` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| exercise_id | string | 0 | `af414c5e-dcb7-4598-8e34-c81651a29122`, `ef746855-e3b5-47f0-b8f1-352666ec3b71` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| wind_speed_unit | string | 0 | `km/h` |
| forecast_time | floating | 2 | _(no data)_ |
| wind_speed | floating | 0 | `13.0`, `3.0` |
| icon_info_id | integer | 0 | `2`, `1` |
| datauuid | string | 0 | `bded4c6f-f329-45bf-9516-f2449b80f66b`, `20f96bb7-84ae-4f2e-9a01-8adca7998fd9` |

---

## `com.samsung.shealth.food_goal.20260607134546.csv`

- Data type: `com.samsung.shealth.food_goal`
- Total rows (approx.): **3** · Columns: **11** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2020-06-22 19:50:34.562`, `2020-06-22 19:50:34.643`, `2020-06-22 19:50:34.571` |
| create_time | datetime (text) | 0 | `2020-06-22 19:50:34.562`, `2020-06-22 19:50:34.643`, `2020-06-22 19:50:34.571` |
| goal_value | floating | 0 | `1285.0` |
| goal_by | floating | 3 | _(no data)_ |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `J5dfK60+5D` |
| comment | floating | 3 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| set_time | integer | 0 | `1592855434513`, `1592855434490`, `1592855434486` |
| datauuid | string | 0 | `696d399d-56b5-4cbb-867e-d8a3f78e3785`, `607b568e-c784-4264-988f-6065518c9fae`, `d4d51c22-b83b-4af0-a644-450bbffb1a41` |
| goal_type | integer | 0 | `0` |

---

## `com.samsung.shealth.goal_history.20260607134546.csv`

- Data type: `com.samsung.shealth.goal_history`
- Total rows (approx.): **2** · Columns: **9** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2020-03-14 02:49:55.089`, `2019-05-31 03:34:42.595` |
| create_time | datetime (text) | 0 | `2020-03-14 02:49:55.089`, `2019-05-31 03:34:42.595` |
| type | integer | 0 | `1` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `J5dfK60+5D` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| set_time | integer | 0 | `1584154194593`, `1559273676439` |
| controller_id | string | 0 | `goal.activity` |
| datauuid | string | 0 | `e9005256-7ea1-4ac1-b0b4-daa1a5eaadd6`, `8a83fc0a-6bb3-4e52-a62f-c63d5548ef75` |

---

## `com.samsung.shealth.insight.message_notification.20260607134546.csv`

- Data type: `com.samsung.shealth.insight.message_notification`
- Total rows (approx.): **3** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| message_id | string | 0 | `Sleep_Weekly_2_2_new`, `Sleep_Weekly_2_1_new` |
| device_type | integer | 0 | `1` |
| status | integer | 0 | `1` |
| update_time | datetime (text) | 0 | `2024-07-25 22:33:42.014`, `2024-07-25 22:33:42.057`, `2024-09-16 17:57:57.853` |
| create_time | datetime (text) | 0 | `2024-07-25 22:33:42.014`, `2024-07-25 22:33:42.057`, `2024-09-16 17:57:57.853` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| issue_time | floating | 3 | _(no data)_ |
| datauuid | string | 0 | `7daf8fd5-373b-473b-aea1-ad96f3c019f3`, `925dc734-fa06-4ad9-8e27-c11cecfc6d3a`, `25897552-d66b-46b6-be25-937446829292` |

---

## `com.samsung.shealth.insight_message.20260607134546.csv`

- Data type: `com.samsung.shealth.insight_message`
- Total rows (approx.): **117** · Columns: **17** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 117 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| is_ai_generated | integer | 0 | `0` |
| feedback_type | integer | 0 | `0` |
| service_id | string | 0 | `tracker.vitality` |
| description | string | 0 | `You had 134 more minutes of movement com...`, `Lately, you've maintained a sleeping HRV...`, `Your heart rate, REM sleep, and sleeping...` |
| exposure_uri | string | 0 | `intent:#Intent;action=com.samsung.androi...`, `intent:#Intent;action=com.samsung.androi...`, `intent:#Intent;action=com.samsung.androi...` |
| condition_id | string | 0 | `active_time_81`, `shrv_balance_58`, `behavior_check_before_sleep_72` |
| msg_id | string | 0 | `AT-12-5`, `HV-3-4`, `SHT-2` |
| update_time | string | 0 | `2025-12-03 14:50:11.381`, `2025-12-04 15:03:30.393`, `2025-12-05 14:22:55.612` |
| create_time | string | 0 | `2025-12-03 14:50:11.381`, `2025-12-04 15:03:30.393`, `2025-12-05 14:22:55.612` |
| is_viewed | integer | 0 | `0` |
| tag | integer | 0 | `32625`, `32532`, `32610` |
| category | string | 0 | `VS_VITALITYSCORE` |
| title | string | 0 | `Find your best routine`, `You're stressing less`, `Sleep is compromised` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `7fd3ab40-ea1c-4686-9ee5-cbaf723fabe3`, `d6b6bf53-d2cb-4043-b50d-9766565bb0d7`, `76f75d09-7bab-4b44-8acb-3e96cfc5fd1e` |
| day_time | integer | 0 | `1764720000000`, `1764806400000`, `1764892800000` |

---

## `com.samsung.shealth.mood.20260607134546.csv`

- Data type: `com.samsung.shealth.mood`
- Total rows (approx.): **5** · Columns: **16** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 5 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `63051050`, `63060070`, `63070030` |
| start_time | string | 0 | `2025-11-06 16:59:59.000`, `2025-11-09 03:15:48.293`, `2025-11-13 02:45:57.812` |
| factors | string | 1 | `16, 17`, `3`, `15, 3` |
| mood_type | integer | 0 | `3`, `2` |
| modify_sh_ver | integer | 0 | `63051050`, `63060070`, `63070030` |
| update_time | string | 0 | `2025-11-06 11:01:17.696`, `2025-11-09 03:15:48.305`, `2025-11-13 02:45:57.820` |
| create_time | string | 0 | `2025-11-06 11:01:17.696`, `2025-11-09 03:15:48.305`, `2025-11-13 02:45:57.820` |
| data_version | integer | 0 | `2` |
| notes | floating | 5 | _(no data)_ |
| place | floating | 5 | _(no data)_ |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| company | floating | 5 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| emotions | string | 1 | `11, 9`, `21, 24, 27, 29, 9`, `29, 31` |
| datauuid | string | 0 | `6f6d7781-1c43-4f40-8cfb-ca6db3a05895`, `c192e2e2-1cff-4e35-a946-b69bb90a54b5`, `c1d499ff-cc48-4b14-9807-0747a174f607` |

---

## `com.samsung.shealth.permission.20260607134546.csv`

- Data type: `com.samsung.shealth.permission`
- Total rows (approx.): **2** · Columns: **12** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| client_id | string | 0 | `com.sec.android.app.shealth` |
| allowed | integer | 0 | `1` |
| update_time | datetime (text) | 0 | `2022-03-24 17:06:47.445`, `2021-09-07 12:27:19.321` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:24.830`, `2021-09-07 12:26:46.164` |
| item | string | 0 | `data` |
| requester | floating | 2 | _(no data)_ |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `UUqPkhoTUZ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| operation | string | 0 | `sync` |
| permitted_on | integer | 0 | `1` |
| datauuid | string | 0 | `1f190ad9-40f2-9f2e-f2ba-6514109f1ef9`, `6d7698b2-a916-bf6f-dac8-1b9a0f99d751` |
| optionals | string | 1 | `6d7698b2-a916-bf6f-dac8-1b9a0f99d751.opt...` |

---

## `com.samsung.shealth.preferences.20260607134546.csv`

- Data type: `com.samsung.shealth.preferences`
- Total rows (approx.): **69** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 69 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| text_value | string | 58 | `{"timestamp":1676994985752,"vo2Max":46.4...`, `diaz.obando.santiago@gmail.com`, `{"fri":true,"mon":true,"sat":false,"sun"...` |
| service_id | string | 26 | `tracker.exercise`, `tracker.heartrate`, `tracker.spo2` |
| float_value | floating | 67 | `1519.0`, `3055.0` |
| update_time | datetime (text) | 0 | `2026-04-19 15:25:57.340`, `2022-08-04 17:39:36.896`, `2022-08-04 17:39:36.894` |
| create_time | datetime (text) | 0 | `2024-06-27 21:20:34.712`, `2022-03-24 17:06:48.003`, `2022-03-24 17:06:48.004` |
| long_value | floating | 66 | `1736921556549.0`, `1738760494700.0`, `1749772800000.0` |
| tag | floating | 69 | _(no data)_ |
| blob_value | string | 59 | `34-favorite_list.blob_value.json`, `34-workout_list.blob_value.json`, `34-favorite_list2.blob_value.json` |
| int_value | floating | 25 | `0.0`, `1.0`, `46.0` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `UUqPkhoTUZ`, `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| double_value | floating | 69 | _(no data)_ |
| datauuid | string | 0 | `settings.marketing_agreement`, `34-favorite_list`, `34-workout_list` |

---

## `com.samsung.shealth.program.sleep_coaching.mission.20260607134546.csv`

- Data type: `com.samsung.shealth.program.sleep_coaching.mission`
- Total rows (approx.): **126** · Columns: **15** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 126 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 126 | _(no data)_ |
| answer | floating | 126 | _(no data)_ |
| priority | integer | 0 | `10`, `11`, `2` |
| modify_sh_ver | floating | 126 | _(no data)_ |
| update_time | datetime (text) | 0 | `2023-11-23 16:49:54.920`, `2023-11-23 16:49:54.921`, `2023-12-10 01:16:44.196` |
| create_time | datetime (text) | 0 | `2023-11-23 16:49:54.920`, `2023-11-23 16:49:54.921`, `2023-11-23 16:49:54.922` |
| data_version | integer | 0 | `2` |
| day_index | integer | 0 | `0`, `1`, `2` |
| mission_id | string | 0 | `HB_10`, `HB_11`, `HB_02` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| is_key_habit | integer | 0 | `1`, `0` |
| session_id | string | 0 | `275c008c-bb3b-4e5a-ada2-c36f825e0c50` |
| datauuid | string | 0 | `9055eb94-8f52-46f4-9520-00a0821e9f52`, `86ae9380-920b-4d62-bf3f-d36b49403a89`, `a752bf18-263e-41cf-8f36-22c0bf03563c` |
| is_done | integer | 0 | `0`, `3`, `1` |

---

## `com.samsung.shealth.program.sleep_coaching.session.20260607134546.csv`

- Data type: `com.samsung.shealth.program.sleep_coaching.session`
- Total rows (approx.): **1** · Columns: **15** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 1 | _(no data)_ |
| mission_count | integer | 0 | `126` |
| is_report_read | integer | 0 | `1` |
| start_date | datetime (text) | 0 | `2023-11-24 00:00:00.000` |
| survey | string | 0 | `275c008c-bb3b-4e5a-ada2-c36f825e0c50.sur...` |
| modify_sh_ver | floating | 1 | _(no data)_ |
| update_time | datetime (text) | 0 | `2023-12-20 13:10:09.556` |
| create_time | datetime (text) | 0 | `2023-11-23 16:49:54.967` |
| data_version | integer | 0 | `3` |
| type | integer | 0 | `3` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| contents_version | integer | 0 | `3` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_date | datetime (text) | 0 | `2023-12-14 00:00:00.000` |
| datauuid | string | 0 | `275c008c-bb3b-4e5a-ada2-c36f825e0c50` |

---

## `com.samsung.shealth.report.20260607134546.csv`

- Data type: `com.samsung.shealth.report`
- Total rows (approx.): **243** · Columns: **12** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 243 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| timezone | string | 0 | `America/Bogota` |
| start_date | integer | 0 | `1644728400000`, `1594011600000`, `1576472400000` |
| update_time | datetime (text) | 0 | `2022-02-26 21:01:41.243`, `2020-07-13 20:20:44.621`, `2019-12-23 18:37:39.717` |
| create_time | datetime (text) | 0 | `2022-02-26 21:01:40.144`, `2020-07-13 20:20:37.126`, `2019-12-23 18:37:37.799` |
| type | integer | 0 | `0` |
| is_empty | integer | 0 | `0`, `1` |
| version | integer | 0 | `2`, `3` |
| deviceuuid | string | 0 | `UUqPkhoTUZ`, `J5dfK60+5D`, `1kGlEKqwGK` |
| content | string | 0 | `X` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `dbd07f15-e957-4f48-9799-e3ab9691f33b`, `b7cf8bdb-c815-4079-af51-9c274c63341b`, `673e409b-df52-4b0a-a7e6-3c68d0093fb9` |
| compressed_content | string | 0 | `dbd07f15-e957-4f48-9799-e3ab9691f33b.com...`, `b7cf8bdb-c815-4079-af51-9c274c63341b.com...`, `673e409b-df52-4b0a-a7e6-3c68d0093fb9.com...` |

---

## `com.samsung.shealth.rewards.20260607134546.csv`

- Data type: `com.samsung.shealth.rewards`
- Total rows (approx.): **758** · Columns: **18** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 758 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| number_of_streak | floating | 731 | `1203.0`, `1205.0`, `33.0` |
| start_time | datetime (text) | 22 | `2019-12-28 18:12:00.162`, `2019-06-25 02:32:05.649`, `2019-11-24 23:02:51.285` |
| exercise_type | floating | 737 | `10007.0`, `1002.0`, `10001.0` |
| device_type | floating | 256 | `10009.0`, `10399999.0`, `100003.0` |
| exercise_session_id | string | 737 | `766d3135-eea4-4dd4-ae55-b1594c2d7d04`, `5c13d72f-ca89-4a59-876f-5bd52802ae4c`, `352abdf7-d8e4-40ce-9530-1869e839bdfc` |
| update_time | datetime (text) | 0 | `2023-07-25 10:26:25.588`, `2020-01-04 22:50:00.394`, `2019-06-25 18:09:45.993` |
| create_time | datetime (text) | 0 | `2019-05-31 03:34:44.839`, `2019-12-28 18:12:00.199`, `2019-06-24 21:26:35.563` |
| source_pkg_name | floating | 758 | _(no data)_ |
| program_id | string | 752 | `186317fc-f87e-46f4-89c2-ff847025f870`, `bbe84f32-2934-4f02-a739-afaaf5dbc475`, `569945ba-52b3-46d7-bbe0-a76d84e7127d` |
| title | string | 0 | `LAST_SLEEP_CHECKING_TIME`, `goal_activity_reward_goal_achieved`, `goal_activity_reward_most_active_day` |
| time_offset | string | 1 | `UTC-0500` |
| extra_data | string | 2 | `{"mIsCompleted":false,"mValue":95,"mValu...`, `{"mIsCompleted":false,"mValue":103,"mVal...`, `{"mIsCompleted":false,"mValue":64,"mValu...` |
| deviceuuid | string | 0 | `J5dfK60+5D`, `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| controller_id | string | 0 | `Sleep.Goal.Temp`, `goal.activity`, `sport.tracker.best.record.duration.lifet...` |
| end_time | datetime (text) | 0 | `2023-07-25 05:00:00.000`, `2019-12-28 18:12:00.162`, `2019-06-24 21:26:35.496` |
| datauuid | string | 0 | `9f77e505-e0d8-4703-bf19-8b2fd8682742`, `e2878e23-ec94-4459-8351-53bee6d44a1e`, `2ced73bd-aec6-4e68-b910-910583380749` |
| is_visible | integer | 0 | `-10000`, `0`, `1` |

---

## `com.samsung.shealth.service_preferences.20260607134546.csv`

- Data type: `com.samsung.shealth.service_preferences`
- Total rows (approx.): **23** · Columns: **14** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 23 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| text_value | string | 21 | `{"05-measure.period":2,"05-alert.high.en...` |
| service_id | string | 1 | `app.settings`, `tracker.daily_activity`, `tracker.cycle` |
| float_value | floating | 23 | _(no data)_ |
| update_time | datetime (text) | 0 | `2025-03-16 15:46:00.408`, `2025-04-04 04:30:04.828`, `2025-01-15 13:13:19.390` |
| create_time | datetime (text) | 0 | `2024-07-17 00:08:00.280`, `2024-07-17 00:08:00.463`, `2024-07-17 03:26:24.957` |
| long_value | floating | 8 | `1736928799383.0`, `1736847462912.0`, `1736933397334.0` |
| key | string | 0 | `psm_plus_settings`, `psm_plus_enable`, `daily_activity_yesterday_all_target_chec...` |
| tag | floating | 23 | _(no data)_ |
| blob_value | floating | 23 | _(no data)_ |
| int_value | floating | 17 | `0.0`, `1.0` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ`, `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| double_value | floating | 23 | _(no data)_ |
| datauuid | string | 0 | `be015ee2-9794-462e-a6cd-aebcb36284b2`, `0dd63ca6-26b8-42d7-98a1-928fd10269c3`, `260a3802-826f-43ba-a81a-ea35b16cfea5` |

---

## `com.samsung.shealth.sleep.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep`
- Total rows (approx.): **1329** · Columns: **62** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1329 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| total_sleep_time_weight | floating | 1009 | `34.0` |
| original_efficiency | floating | 1329 | _(no data)_ |
| mental_recovery | floating | 28 | `59.0`, `73.0`, `66.0` |
| wake_score | floating | 1009 | `9.0`, `10.0`, `5.0` |
| factor_01 | floating | 28 | `16.0`, `0.0`, `23.0` |
| factor_02 | floating | 28 | `32.0`, `0.0`, `44.0` |
| factor_03 | floating | 28 | `7.0`, `29.0`, `13.0` |
| factor_04 | floating | 28 | `6.0`, `2.0`, `9.0` |
| factor_05 | floating | 28 | `48.0`, `35.0`, `30.0` |
| factor_06 | floating | 28 | `384.0`, `130.0`, `367.0` |
| factor_07 | floating | 28 | `87.0`, `112.0`, `151.0` |
| factor_08 | floating | 28 | `2.0`, `0.0`, `1.0` |
| factor_09 | floating | 28 | `29.0`, `25.0`, `14.0` |
| factor_10 | floating | 652 | `0.0`, `1.0`, `9.0` |
| deep_score | floating | 1009 | `12.0`, `9.0`, `11.0` |
| integrated_id | floating | 1329 | _(no data)_ |
| latency_weight | floating | 1009 | `16.0` |
| has_sleep_data | integer | 0 | `0`, `1` |
| bedtime_detection_delay | floating | 709 | `900000.0`, `780000.0`, `1200000.0` |
| sleep_efficiency_with_latency | floating | 1009 | `85.0`, `86.0`, `67.0` |
| wakeup_time_detection_delay | floating | 709 | `1500000.0`, `780000.0`, `1740000.0` |
| total_rem_duration | floating | 705 | `88.0`, `107.0`, `104.0` |
| combined_id | string | 1199 | `0a0657db-4aae-4bab-b220-2bb3332fa7a6`, `f3261727-0dc2-48a7-bc26-ab834e17c77d`, `b0583fca-9baa-42aa-8caf-2ac90c199afe` |
| nap_score | floating | 1110 | `0.0`, `1.0`, `2.0` |
| sleep_type | floating | 373 | `-1.0`, `3.0` |
| sleep_latency | floating | 709 | `-1.0`, `3240000.0`, `1260000.0` |
| data_version | floating | 25 | `3.0`, `4.0`, `6.0` |
| latency_score | floating | 1009 | `16.0`, `3.0`, `9.0` |
| deep_weight | floating | 1009 | `15.0`, `18.0` |
| rem_weight | floating | 1009 | `23.0`, `26.0` |
| physical_recovery | floating | 28 | `54.0`, `13.0`, `55.0` |
| original_wake_up_time | datetime (text) | 875 | `2023-10-31 10:34:00.000`, `2023-11-01 10:37:00.000`, `2023-11-03 10:50:00.000` |
| movement_awakening | floating | 28 | `28.0`, `72.0`, `21.0` |
| is_integrated | floating | 1329 | _(no data)_ |
| original_bed_time | datetime (text) | 875 | `2023-10-31 05:56:00.000`, `2023-11-01 05:04:00.000`, `2023-11-03 04:22:00.000` |
| goal_bed_time | floating | 868 | `84600000.0`, `82800000.0` |
| quality | floating | 1305 | `0.0` |
| extra_data | string | 649 | `8a7054e7-026c-492b-9b4d-119fc5e032fd.ext...`, `22b7480c-84db-42ba-a945-ffdc2f71665c.ext...`, `779ff40f-63fa-4129-87cd-e0c18f859831.ext...` |
| wake_weight | floating | 1009 | `12.0`, `6.0` |
| rem_score | floating | 1009 | `2.0`, `19.0`, `9.0` |
| goal_wake_up_time | floating | 868 | `27000000.0`, `25200000.0` |
| sleep_cycle | floating | 28 | `3.0`, `1.0`, `4.0` |
| total_light_duration | floating | 705 | `147.0`, `238.0`, `246.0` |
| efficiency | floating | 1 | `0.0`, `87.0`, `73.0` |
| sleep_score | floating | 28 | `70.0`, `52.0`, `72.0` |
| sleep_duration | floating | 27 | `384.0`, `130.0`, `367.0` |
| stage_analyzed_type | floating | 705 | `1.0`, `2.0` |
| total_sleep_time_score | floating | 1009 | `25.0`, `30.0`, `6.0` |
| com.samsung.health.sleep.create_sh_ver | floating | 520 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.sleep.start_time | datetime (text) | 0 | `2022-03-26 03:40:00.000`, `2022-07-12 03:10:00.000`, `2022-07-14 03:20:00.000` |
| com.samsung.health.sleep.custom | floating | 1329 | _(no data)_ |
| com.samsung.health.sleep.modify_sh_ver | floating | 520 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.sleep.update_time | datetime (text) | 0 | `2022-03-26 11:03:48.217`, `2022-07-12 21:36:43.917`, `2022-07-14 13:41:29.082` |
| com.samsung.health.sleep.create_time | datetime (text) | 0 | `2022-03-26 11:03:48.217`, `2022-07-12 21:36:43.917`, `2022-07-14 13:41:29.082` |
| com.samsung.health.sleep.client_data_id | floating | 1329 | _(no data)_ |
| com.samsung.health.sleep.client_data_ver | floating | 1329 | _(no data)_ |
| com.samsung.health.sleep.time_offset | string | 0 | `UTC-0500` |
| com.samsung.health.sleep.deviceuuid | string | 0 | `1kGlEKqwGK`, `Cv7sH/e0hQ` |
| com.samsung.health.sleep.comment | floating | 1329 | _(no data)_ |
| com.samsung.health.sleep.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.health.sleep.end_time | datetime (text) | 0 | `2022-03-26 10:40:00.000`, `2022-07-12 10:20:00.000`, `2022-07-14 10:30:00.000` |
| com.samsung.health.sleep.datauuid | string | 0 | `0a065d78-b919-4c0e-a74e-8fc8a9249957`, `fcfc77fe-d59b-4ac3-b6c1-095568d5e0bb`, `e5b34154-802e-4b49-9a19-01778ce1eca5` |

---

## `com.samsung.shealth.sleep_combined.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep_combined`
- Total rows (approx.): **64** · Columns: **55** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 64 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| total_sleep_time_weight | floating | 51 | `34.0` |
| original_efficiency | floating | 64 | _(no data)_ |
| create_sh_ver | floating | 30 | `62600630.0`, `62610110.0`, `62660010.0` |
| start_time | string | 0 | `2022-08-09 04:14:00.000`, `2022-08-24 02:54:00.000`, `2023-01-27 04:59:00.000` |
| mental_recovery | floating | 0 | `34.0`, `69.0`, `48.0` |
| wake_score | floating | 51 | `3.0`, `7.0`, `6.0` |
| factor_01 | integer | 0 | `35`, `0`, `43` |
| factor_02 | integer | 0 | `78`, `51`, `72` |
| factor_03 | integer | 0 | `0`, `11`, `8` |
| factor_04 | integer | 0 | `26`, `6`, `22` |
| factor_05 | integer | 0 | `52`, `31`, `53` |
| factor_06 | integer | 0 | `303`, `400`, `447` |
| factor_07 | integer | 0 | `97`, `112`, `168` |
| factor_08 | integer | 0 | `2`, `1`, `0` |
| factor_09 | integer | 0 | `37`, `19`, `34` |
| factor_10 | floating | 24 | `0.0`, `1.0`, `21.0` |
| deep_score | floating | 51 | `10.0`, `11.0`, `12.0` |
| latency_weight | floating | 51 | `16.0` |
| has_sleep_data | integer | 0 | `0` |
| sleep_efficiency_with_latency | floating | 51 | `72.0`, `77.0`, `79.0` |
| total_rem_duration | floating | 40 | `78.0`, `33.0`, `54.0` |
| modify_sh_ver | floating | 30 | `62600630.0`, `62610110.0`, `62660010.0` |
| update_time | string | 0 | `2022-08-09 10:06:29.049`, `2022-08-24 10:03:38.663`, `2023-01-27 12:50:10.752` |
| nap_score | floating | 54 | `0.0` |
| create_time | string | 0 | `2022-08-09 10:06:29.049`, `2022-08-24 10:03:38.663`, `2023-01-27 12:50:10.752` |
| client_data_id | floating | 64 | _(no data)_ |
| sleep_type | floating | 38 | `-1.0`, `3.0` |
| data_version | integer | 0 | `3`, `4`, `6` |
| latency_score | floating | 51 | `6.0`, `14.0`, `16.0` |
| deep_weight | floating | 51 | `15.0`, `18.0` |
| rem_weight | floating | 51 | `23.0`, `26.0` |
| physical_recovery | floating | 0 | `70.0`, `53.0`, `71.0` |
| original_wake_up_time | floating | 64 | _(no data)_ |
| client_data_ver | floating | 64 | _(no data)_ |
| movement_awakening | floating | 0 | `29.0`, `22.0`, `24.0` |
| original_bed_time | floating | 64 | _(no data)_ |
| goal_bed_time | floating | 34 | `84600000.0` |
| quality | floating | 24 | `0.0` |
| time_offset | string | 0 | `UTC-0500` |
| extra_data | floating | 64 | _(no data)_ |
| wake_weight | floating | 51 | `12.0`, `6.0` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ`, `1kGlEKqwGK` |
| rem_score | floating | 51 | `14.0`, `13.0`, `5.0` |
| goal_wake_up_time | floating | 34 | `27000000.0` |
| sleep_cycle | integer | 0 | `2`, `3`, `4` |
| total_light_duration | floating | 40 | `192.0`, `203.0`, `225.0` |
| efficiency | floating | 0 | `82.0`, `92.0`, `88.0` |
| sleep_score | integer | 0 | `58`, `71`, `62` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| sleep_duration | integer | 0 | `303`, `400`, `447` |
| stage_analyzed_type | floating | 40 | `1.0`, `2.0` |
| end_time | string | 0 | `2022-08-09 10:00:00.000`, `2022-08-24 09:59:00.000`, `2023-01-27 12:40:00.000` |
| datauuid | string | 0 | `0a0657db-4aae-4bab-b220-2bb3332fa7a6`, `f3261727-0dc2-48a7-bc26-ab834e17c77d`, `b0583fca-9baa-42aa-8caf-2ac90c199afe` |
| stage_analysis_type | floating | 64 | _(no data)_ |
| total_sleep_time_score | floating | 51 | `18.0`, `24.0`, `27.0` |

---

## `com.samsung.shealth.sleep_data.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep_data`
- Total rows (approx.): **3** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 3 | _(no data)_ |
| start_time | datetime (text) | 0 | `2022-07-29 04:49:00.000`, `2022-09-22 10:42:00.000`, `2023-10-26 11:11:00.000` |
| modify_sh_ver | floating | 3 | _(no data)_ |
| update_time | datetime (text) | 0 | `2022-07-29 06:03:41.424`, `2022-09-22 10:59:57.319`, `2023-10-26 11:28:12.095` |
| create_time | datetime (text) | 0 | `2022-07-29 06:03:41.424`, `2022-09-22 10:59:57.319`, `2023-10-26 11:28:12.095` |
| sleep_uuid | string | 0 | `779ff40f-63fa-4129-87cd-e0c18f859831`, `7cb09d60-275b-45c1-8461-c68179189ad9`, `72f57a8d-4374-4f7d-b7ed-e1144433f963` |
| sleep_status | string | 0 | `72073281-dc3d-4abf-ae87-73a7a32c1ae7.sle...`, `2039c491-459d-4095-a21d-28007eefb060.sle...`, `b9cde5c5-defa-4e55-aee2-b3bc301b2aae.sle...` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| comment | floating | 3 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| json_version | integer | 0 | `1` |
| datauuid | string | 0 | `72073281-dc3d-4abf-ae87-73a7a32c1ae7`, `2039c491-459d-4095-a21d-28007eefb060`, `b9cde5c5-defa-4e55-aee2-b3bc301b2aae` |

---

## `com.samsung.shealth.sleep_goal.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep_goal`
- Total rows (approx.): **1** · Columns: **11** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 1 | _(no data)_ |
| modify_sh_ver | floating | 1 | _(no data)_ |
| update_time | datetime (text) | 0 | `2023-11-23 16:48:48.681` |
| create_time | datetime (text) | 0 | `2023-11-23 16:48:48.681` |
| sleep_time | integer | 0 | `-57600000` |
| wake_up_time | integer | 0 | `27000000` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| bed_time | integer | 0 | `84600000` |
| set_time | datetime (text) | 0 | `2023-11-23 16:48:48.670` |
| datauuid | string | 0 | `1c0ffd23-e5e1-417a-8068-ad8cea00194a` |

---

## `com.samsung.shealth.sleep_raw_data.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep_raw_data`
- Total rows (approx.): **5** · Columns: **10** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 5 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `63200011` |
| modify_sh_ver | integer | 0 | `63200011` |
| update_time | datetime (text) | 0 | `2026-06-01 13:48:37.195`, `2026-06-02 13:17:30.141`, `2026-06-03 13:26:29.610` |
| create_time | datetime (text) | 0 | `2026-06-01 13:48:37.195`, `2026-06-02 13:17:30.141`, `2026-06-03 13:26:29.610` |
| sleep_uuid | string | 0 | `594c0b45-9857-48c3-88bb-cb3bf0ddd834`, `fb3f8d46-a015-411e-8e83-e1605dbfcc03`, `6e6738c8-aa9f-49c9-a584-79b5544c6344` |
| data | string | 0 | `f7e88d57-c4cd-4a82-8897-0ac531a67994.dat...`, `5957a736-d9c4-4453-9ac9-2d2d8a22fd63.dat...`, `4dd72c6a-80d9-4613-82a7-7383223c5bae.dat...` |
| version | integer | 0 | `2` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `f7e88d57-c4cd-4a82-8897-0ac531a67994`, `5957a736-d9c4-4453-9ac9-2d2d8a22fd63`, `4dd72c6a-80d9-4613-82a7-7383223c5bae` |

---

## `com.samsung.shealth.sleep_snoring.20260607134546.csv`

- Data type: `com.samsung.shealth.sleep_snoring`
- Total rows (approx.): **33** · Columns: **12** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 33 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| duration | integer | 0 | `0` |
| create_sh_ver | floating | 12 | `62610110.0`, `62930070.0`, `62950170.0` |
| start_time | datetime (text) | 0 | `2022-07-31 08:59:22.494`, `2023-01-18 06:22:07.698`, `2023-05-10 03:55:59.145` |
| custom | string | 28 | `8cc225ea-7231-45e4-8812-6a5ba8231799.cus...`, `56ad8b28-e7cb-4bec-a49a-f4e9e0db386a.cus...`, `a60eb935-3858-4656-838c-71fcf464fc35.cus...` |
| modify_sh_ver | floating | 12 | `62610110.0`, `62930070.0`, `62950170.0` |
| update_time | datetime (text) | 0 | `2022-07-31 09:10:51.174`, `2023-01-18 12:50:14.805`, `2023-05-10 10:31:21.755` |
| create_time | datetime (text) | 0 | `2022-07-31 09:10:51.174`, `2023-01-18 12:50:14.805`, `2023-05-10 10:31:21.755` |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | datetime (text) | 0 | `2022-07-31 09:10:51.132`, `2023-01-18 12:50:14.654`, `2023-05-10 10:31:21.689` |
| datauuid | string | 0 | `b65c454f-502c-4263-bf25-4560a929eb1e`, `1d6a4d29-b206-46b0-b86f-2581ab4afca2`, `60cf386a-c76c-4146-abcf-480f38ac08a0` |

---

## `com.samsung.shealth.social.friends.20260607134546.csv`

- Data type: `com.samsung.shealth.social.friends`
- Total rows (approx.): **5** · Columns: **16** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 5 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| nick_name | string | 0 | `alex.diaz.nieto78`, `Jenniffer Angel`, `Mariana` |
| device_type | string | 0 | `ANDROID` |
| msisdn | floating | 1 | `573134923363.0`, `573138381251.0`, `573193486459.0` |
| status | integer | 0 | `0` |
| image_url | string | 3 | `https://d3tqs16tcqd0gr.cloudfront.net/1b...`, `https://d3tqs16tcqd0gr.cloudfront.net/57...` |
| update_time | datetime (text) | 0 | `2022-03-24 17:07:02.881`, `2023-08-25 22:01:11.144`, `2022-09-08 18:50:28.707` |
| create_time | datetime (text) | 0 | `2022-03-24 17:07:02.881`, `2022-06-18 18:50:21.267`, `2022-09-08 18:50:28.707` |
| blocked | integer | 0 | `0` |
| uid | integer | 0 | `42363944`, `42362639`, `85738829` |
| level | integer | 0 | `1`, `2` |
| gdpr_restricted | integer | 0 | `0` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| invitation_allowed | integer | 0 | `0` |
| display_name | string | 0 | `Tio Alex`, `Jenniffer Angel`, `Mariana Pacheco` |
| datauuid | string | 0 | `f6c17465-62a9-44a4-89a6-65f454b792a9`, `b0134815-0c1d-40a3-916f-ab5f11dfcdb7`, `0becac01-1c2e-4fce-b79f-4d21517f1be2` |

---

## `com.samsung.shealth.social.leaderboard.20260607134546.csv`

- Data type: `com.samsung.shealth.social.leaderboard`
- Total rows (approx.): **3** · Columns: **9** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2024-10-24 02:57:50.394`, `2024-10-24 02:57:50.430`, `2025-11-06 11:00:17.857` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:59.479`, `2022-03-24 17:06:59.509`, `2022-03-24 17:06:59.546` |
| my_value | integer | 0 | `53`, `54`, `1` |
| body | string | 0 | `18e030f3-283b-4981-b976-35cb52af9e76.bod...`, `a8fd7e36-3829-4466-95b8-2650b110dc49.bod...`, `f3339ce3-03f1-4450-88d2-b08e04dafcd2.bod...` |
| type | integer | 0 | `102`, `101`, `200` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| last_sync_time | integer | 0 | `1729738670356`, `1729738670361`, `1762426817843` |
| datauuid | string | 0 | `18e030f3-283b-4981-b976-35cb52af9e76`, `a8fd7e36-3829-4466-95b8-2650b110dc49`, `f3339ce3-03f1-4450-88d2-b08e04dafcd2` |

---

## `com.samsung.shealth.social.public_challenge.20260607134546.csv`

- Data type: `com.samsung.shealth.social.public_challenge`
- Total rows (approx.): **1** · Columns: **7** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2025-11-06 11:00:17.539` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:59.264` |
| body | string | 0 | `0e3a9f1e-1cbb-4650-bfe3-6e6b85b8238a.bod...` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| last_sync_time | integer | 0 | `0` |
| datauuid | string | 0 | `0e3a9f1e-1cbb-4650-bfe3-6e6b85b8238a` |

---

## `com.samsung.shealth.social.public_challenge.extra.20260607134546.csv`

- Data type: `com.samsung.shealth.social.public_challenge.extra`
- Total rows (approx.): **1** · Columns: **7** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2022-03-24 17:06:50.098` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:50.098` |
| type | integer | 0 | `2` |
| value | string | 0 | `{"uiViewStatusItemList":[]}` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `c7ca3ee3-0e1c-413a-b921-bf59b5201535` |

---

## `com.samsung.shealth.social.public_challenge.history.20260607134546.csv`

- Data type: `com.samsung.shealth.social.public_challenge.history`
- Total rows (approx.): **1** · Columns: **8** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2025-11-06 11:00:17.890` |
| create_time | datetime (text) | 0 | `2022-03-24 17:06:59.528` |
| body | string | 0 | `247811e8-ab78-4b0a-b3f9-4e3e94aade0c.bod...` |
| challenge_time | string | 0 | `SIMPLE_LEVEL` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| last_sync_time | integer | 0 | `1762426817885` |
| datauuid | string | 0 | `247811e8-ab78-4b0a-b3f9-4e3e94aade0c` |

---

## `com.samsung.shealth.social.service_status.20260607134546.csv`

- Data type: `com.samsung.shealth.social.service_status`
- Total rows (approx.): **3** · Columns: **7** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 3 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| status | integer | 0 | `200`, `1`, `0` |
| update_time | string | 0 | `2024-12-12 17:27:01.073`, `2022-03-24 17:06:59.522`, `2022-03-24 17:06:50.084` |
| create_time | datetime (text) | 0 | `2022-03-16 12:01:08.554`, `2022-03-16 12:01:08.555` |
| service_type | integer | 0 | `1`, `2`, `3` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `5093e90e-dfa4-4d76-9b69-792257ad2fd1`, `ccd013a3-0f92-48d9-afd4-0f3e65a914ba`, `62667bb9-e5d0-4adc-94ac-974ff537357f` |

---

## `com.samsung.shealth.step_daily_trend.20260607134546.csv`

- Data type: `com.samsung.shealth.step_daily_trend`
- Total rows (approx.): **5508** · Columns: **13** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| binning_data | string | 0 | `c3926ac1-11a7-404d-bc8d-dca32933d50f.bin...`, `d14ba94f-4fb4-49c0-a7d6-f4341b96d9ac.bin...`, `6e2696de-ed57-41a1-9c5b-ab183fb992c5.bin...` |
| update_time | string | 0 | `2022-07-05 01:04:01.714`, `2022-07-05 01:04:01.731`, `2022-07-05 01:04:01.732` |
| create_time | string | 0 | `2022-07-05 01:04:01.714`, `2022-07-05 01:04:01.731`, `2022-07-05 01:04:01.732` |
| source_pkg_name | string | 0 | `com.sec.android.app.shealth` |
| source_type | integer | 0 | `0`, `-2`, `15` |
| count | integer | 0 | `85`, `522`, `3344` |
| speed | floating | 0 | `1.8353161`, `6.9444447`, `2.9149532` |
| distance | floating | 0 | `67.31426`, `440.70358`, `2612.099` |
| calorie | floating | 0 | `3.0053189`, `21.452461`, `120.36032` |
| deviceuuid | string | 0 | `1kGlEKqwGK`, `VfS0qUERdZ`, `gp5ou4ds4l` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `c3926ac1-11a7-404d-bc8d-dca32933d50f`, `d14ba94f-4fb4-49c0-a7d6-f4341b96d9ac`, `6e2696de-ed57-41a1-9c5b-ab183fb992c5` |
| day_time | integer | 0 | `1559692800000`, `1559779200000`, `1559865600000` |

---

## `com.samsung.shealth.stress.20260607134546.csv`

- Data type: `com.samsung.shealth.stress`
- Total rows (approx.): **7243** · Columns: **18** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 1945 | `62600630.0` |
| start_time | string | 0 | `2022-07-01 21:52:13.000`, `2022-07-02 22:21:15.000`, `2022-07-02 22:23:54.000` |
| custom | floating | 2000 | _(no data)_ |
| binning_data | string | 18 | `254b718f-8a49-4e64-8118-a61d87f81e7a.bin...`, `e4494079-b93a-4541-b82a-3311198f0196.bin...`, `2a4952dd-9743-4482-94ad-35ca09b27dc1.bin...` |
| tag_id | integer | 0 | `10000`, `10011` |
| modify_sh_ver | floating | 1945 | `62600630.0` |
| update_time | string | 0 | `2022-07-01 21:52:13.755`, `2022-07-02 22:21:15.706`, `2022-07-02 22:23:54.904` |
| create_time | string | 0 | `2022-07-01 21:52:13.755`, `2022-07-02 22:21:15.706`, `2022-07-02 22:23:54.904` |
| max | floating | 18 | `0.0`, `4.0`, `2.0` |
| min | floating | 18 | `0.0`, `2.0`, `8.0` |
| score | floating | 0 | `92.0`, `95.0`, `42.0` |
| algorithm | floating | 2000 | _(no data)_ |
| time_offset | string | 0 | `UTC-0500` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| comment | floating | 2000 | _(no data)_ |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| end_time | string | 0 | `2022-07-01 21:52:13.000`, `2022-07-02 22:21:15.000`, `2022-07-02 22:23:54.000` |
| datauuid | string | 0 | `8533a30a-9310-41a7-a4c6-cf9a982a03f2`, `9254ad49-b1c0-49e7-b43a-6a0bfbe2765b`, `7eeabbdc-4cf9-45bc-b77c-b1aa7ec54d23` |

---

## `com.samsung.shealth.stress.histogram.20260607134546.csv`

- Data type: `com.samsung.shealth.stress.histogram`
- Total rows (approx.): **1** · Columns: **8** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| update_time | datetime (text) | 0 | `2026-06-07 16:27:00.256` |
| create_time | datetime (text) | 0 | `2022-07-02 22:21:15.532` |
| base_hr | integer | 0 | `60940` |
| decay_time | integer | 0 | `1780847804` |
| deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| histogram | string | 0 | `89add28e-cc60-4096-8ece-a2ae0d5ce4b0.his...` |
| datauuid | string | 0 | `89add28e-cc60-4096-8ece-a2ae0d5ce4b0` |

---

## `com.samsung.shealth.tracker.floors_day_summary.20260607134546.csv`

- Data type: `com.samsung.shealth.tracker.floors_day_summary`
- Total rows (approx.): **200** · Columns: **11** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 200 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | integer | 0 | `62810050`, `62820030`, `62850050` |
| binning_data | string | 159 | `1318982c-e895-4683-ad90-df846c0b61a6.bin...`, `37911a5f-d504-4ce4-844c-ab210fc1ada8.bin...`, `95bb31f4-205b-40e7-b0b3-4d20f03e8f36.bin...` |
| modify_sh_ver | integer | 0 | `62810050`, `62820030`, `62850050` |
| update_time | datetime (text) | 0 | `2024-10-25 05:39:10.183`, `2024-10-25 05:39:10.221`, `2024-10-25 05:39:10.228` |
| create_time | datetime (text) | 0 | `2024-10-25 05:39:10.183`, `2024-10-25 05:39:10.221`, `2024-10-25 05:39:10.228` |
| floor_count | integer | 0 | `0`, `35`, `2` |
| version_code | integer | 0 | `2`, `1` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| datauuid | string | 0 | `1318982c-e895-4683-ad90-df846c0b61a6`, `b26c1964-7b64-454e-97d0-51417085f9a9`, `41e45b15-d2a7-41f7-9fda-a334bc0ee233` |
| day_time | integer | 0 | `1729814400000`, `1660348800000`, `1671321600000` |

---

## `com.samsung.shealth.tracker.heart_rate.20260607134546.csv`

- Data type: `com.samsung.shealth.tracker.heart_rate`
- Total rows (approx.): **65903** · Columns: **21** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| source | floating | 2000 | _(no data)_ |
| tag_id | integer | 0 | `21312`, `21301`, `21311` |
| com.samsung.health.heart_rate.create_sh_ver | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.heart_beat_count | integer | 0 | `1`, `0` |
| com.samsung.health.heart_rate.start_time | datetime (text) | 0 | `2020-06-22 17:00:29.328`, `2020-06-27 18:10:52.068`, `2021-10-27 12:59:13.691` |
| com.samsung.health.heart_rate.custom | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.binning_data | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.modify_sh_ver | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.update_time | datetime (text) | 0 | `2020-06-22 17:10:50.254`, `2020-06-27 18:11:06.557`, `2021-10-27 12:59:24.786` |
| com.samsung.health.heart_rate.create_time | datetime (text) | 0 | `2020-06-22 17:10:50.254`, `2020-06-27 18:11:06.557`, `2021-10-27 12:59:24.786` |
| com.samsung.health.heart_rate.client_data_id | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.max | floating | 1738 | `0.0`, `66.0`, `114.0` |
| com.samsung.health.heart_rate.min | floating | 1738 | `0.0`, `66.0`, `114.0` |
| com.samsung.health.heart_rate.client_data_ver | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.time_offset | string | 0 | `UTC-0500` |
| com.samsung.health.heart_rate.deviceuuid | string | 0 | `gp5ou4ds4l`, `UUqPkhoTUZ`, `Cv7sH/e0hQ` |
| com.samsung.health.heart_rate.comment | floating | 2000 | _(no data)_ |
| com.samsung.health.heart_rate.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.health.heart_rate.end_time | datetime (text) | 0 | `2020-06-22 17:00:29.328`, `2020-06-27 18:10:52.068`, `2021-10-27 12:59:16.904` |
| com.samsung.health.heart_rate.datauuid | string | 0 | `23a7f2ba-379e-7643-6f8f-0312a7a8174d`, `d6370965-305e-d4db-5b80-4ac05e2aec32`, `6ea33a70-84ec-40d7-8d5c-d9980594a6c9` |
| com.samsung.health.heart_rate.heart_rate | floating | 0 | `71.0`, `77.0`, `66.0` |

---

## `com.samsung.shealth.tracker.oxygen_saturation.20260607134546.csv`

- Data type: `com.samsung.shealth.tracker.oxygen_saturation`
- Total rows (approx.): **1297** · Columns: **24** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 1297 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| integrated_id | floating | 1297 | _(no data)_ |
| source | floating | 1297 | _(no data)_ |
| tag_id | integer | 0 | `31000`, `31301` |
| coverage_rate | floating | 1166 | `23.0`, `57.0`, `26.0` |
| com.samsung.health.oxygen_saturation.create_sh_ver | floating | 497 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.oxygen_saturation.start_time | string | 0 | `2022-07-02 23:11:17.236`, `2022-07-03 17:01:14.327`, `2022-07-09 02:27:48.800` |
| com.samsung.health.oxygen_saturation.custom | floating | 1297 | _(no data)_ |
| com.samsung.health.oxygen_saturation.modify_sh_ver | floating | 496 | `62600630.0`, `62610110.0`, `62620030.0` |
| com.samsung.health.oxygen_saturation.update_time | string | 0 | `2022-07-02 23:11:17.245`, `2022-07-03 17:01:14.328`, `2022-07-09 02:27:48.806` |
| com.samsung.health.oxygen_saturation.create_time | string | 0 | `2022-07-02 23:11:17.245`, `2022-07-03 17:01:14.328`, `2022-07-09 02:27:48.806` |
| com.samsung.health.oxygen_saturation.client_data_id | floating | 1297 | _(no data)_ |
| com.samsung.health.oxygen_saturation.low_duration | floating | 5 | `0.0`, `9.0`, `31.0` |
| com.samsung.health.oxygen_saturation.binning | string | 5 | `0d5a558f-cd98-4e56-8190-7ebc7ef351df.com...`, `b82d3bbb-25c8-4c73-99ff-a71097476ef0.com...`, `52431b56-560f-4471-bf92-eaba49411dc0.com...` |
| com.samsung.health.oxygen_saturation.max | floating | 5 | `97.0`, `100.0`, `98.0` |
| com.samsung.health.oxygen_saturation.min | floating | 5 | `90.0`, `89.0`, `88.0` |
| com.samsung.health.oxygen_saturation.spo2 | floating | 0 | `96.0`, `99.0`, `95.0` |
| com.samsung.health.oxygen_saturation.client_data_ver | floating | 1297 | _(no data)_ |
| com.samsung.health.oxygen_saturation.time_offset | string | 0 | `UTC-0500` |
| com.samsung.health.oxygen_saturation.deviceuuid | string | 0 | `Cv7sH/e0hQ` |
| com.samsung.health.oxygen_saturation.comment | floating | 1297 | _(no data)_ |
| com.samsung.health.oxygen_saturation.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.health.oxygen_saturation.end_time | string | 0 | `2022-07-02 23:11:17.236`, `2022-07-03 17:01:14.327`, `2022-07-09 02:27:48.800` |
| com.samsung.health.oxygen_saturation.datauuid | string | 0 | `e0ed1e25-bda0-4046-beaa-f0c302371616`, `d5dbf67c-c612-4a13-ba5f-35f41d91b039`, `a28f1fa8-ac70-4702-a50f-54e7bd8c797e` |
| com.samsung.health.oxygen_saturation.heart_rate | floating | 1292 | `92.0`, `85.0`, `81.0` |

---

## `com.samsung.shealth.tracker.pedometer_day_summary.20260607134546.csv`

- Data type: `com.samsung.shealth.tracker.pedometer_day_summary`
- Total rows (approx.): **5508** · Columns: **21** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| create_sh_ver | floating | 2000 | _(no data)_ |
| step_count | integer | 0 | `353`, `803`, `3373` |
| binning_data | string | 0 | `390b7ae5-e8f3-46f4-9073-227bb0faeb39.bin...`, `3cb8cc88-b1b1-4a23-8c11-4a46f3cb1831.bin...`, `b8d25b4e-e495-4669-aad5-18489f0f2b1e.bin...` |
| active_time | integer | 0 | `165581`, `429754`, `1829801` |
| recommendation | integer | 0 | `6000` |
| modify_sh_ver | floating | 2000 | _(no data)_ |
| run_step_count | integer | 0 | `1`, `12`, `16` |
| update_time | string | 0 | `2020-04-11 02:09:30.873`, `2019-11-20 04:46:16.705`, `2020-01-24 05:00:01.702` |
| source_package_name | string | 0 | `com.sec.android.app.shealth` |
| create_time | string | 0 | `2020-04-10 05:41:08.457`, `2019-11-19 11:56:22.484`, `2020-01-24 05:00:01.702` |
| source_info | string | 1109 | `390b7ae5-e8f3-46f4-9073-227bb0faeb39.sou...`, `3cb8cc88-b1b1-4a23-8c11-4a46f3cb1831.sou...`, `e38a868d-7c33-40c2-a4ae-7d46544bf955.sou...` |
| speed | floating | 0 | `1.8201224`, `1.5281756`, `3.4722223` |
| distance | floating | 0 | `301.37845`, `656.7399`, `2624.75` |
| calorie | floating | 0 | `14.48603`, `31.624878`, `121.442406` |
| walk_step_count | integer | 0 | `352`, `791`, `3357` |
| deviceuuid | string | 0 | `VfS0qUERdZ`, `J5dfK60+5D`, `gp5ou4ds4l` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| healthy_step | integer | 0 | `0`, `341`, `387` |
| achievement | string | 0 | `390b7ae5-e8f3-46f4-9073-227bb0faeb39.ach...`, `3cb8cc88-b1b1-4a23-8c11-4a46f3cb1831.ach...`, `b8d25b4e-e495-4669-aad5-18489f0f2b1e.ach...` |
| datauuid | string | 0 | `390b7ae5-e8f3-46f4-9073-227bb0faeb39`, `3cb8cc88-b1b1-4a23-8c11-4a46f3cb1831`, `b8d25b4e-e495-4669-aad5-18489f0f2b1e` |
| day_time | integer | 0 | `1586476800000`, `1574121600000`, `1579737600000` |

---

## `com.samsung.shealth.tracker.pedometer_step_count.20260607134546.csv`

- Data type: `com.samsung.shealth.tracker.pedometer_step_count`
- Total rows (approx.): **4317** · Columns: **18** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 2000 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| duration | integer | 0 | `7717`, `15901`, `10020` |
| version_code | integer | 0 | `4` |
| run_step | integer | 0 | `0`, `1`, `22` |
| walk_step | integer | 0 | `10`, `25`, `16` |
| com.samsung.health.step_count.start_time | string | 0 | `2026-05-03 07:32:00.000`, `2026-05-03 07:35:00.000`, `2026-05-03 07:36:00.000` |
| com.samsung.health.step_count.sample_position_type | floating | 2000 | _(no data)_ |
| com.samsung.health.step_count.custom | floating | 2000 | _(no data)_ |
| com.samsung.health.step_count.update_time | string | 0 | `2026-05-03 07:35:00.147`, `2026-05-03 07:55:01.157`, `2026-05-03 07:55:01.211` |
| com.samsung.health.step_count.create_time | string | 0 | `2026-05-03 07:35:00.147`, `2026-05-03 07:55:01.157`, `2026-05-03 07:55:01.211` |
| com.samsung.health.step_count.count | integer | 0 | `10`, `25`, `16` |
| com.samsung.health.step_count.speed | floating | 0 | `0.8888889`, `1.1388888`, `1.1666666` |
| com.samsung.health.step_count.distance | floating | 0 | `6.86`, `18.11`, `11.69` |
| com.samsung.health.step_count.calorie | floating | 0 | `0.3`, `0.78`, `0.48` |
| com.samsung.health.step_count.time_offset | string | 0 | `UTC-0500` |
| com.samsung.health.step_count.deviceuuid | string | 0 | `Cv7sH/e0hQ`, `1kGlEKqwGK` |
| com.samsung.health.step_count.pkg_name | string | 0 | `com.sec.android.app.shealth` |
| com.samsung.health.step_count.end_time | string | 0 | `2026-05-03 07:33:00.000`, `2026-05-03 07:36:00.000`, `2026-05-03 07:37:00.000` |
| com.samsung.health.step_count.datauuid | string | 0 | `162ef3a1-077b-4ce0-9ddf-12214e743040`, `8f4408bc-1f47-4e4d-8d72-f6ae58569fbf`, `6d456006-eaf4-4b61-b2d5-4c407d5d641d` |

---

## `com.samsung.shealth.vitality_score.20260607134546.csv`

- Data type: `com.samsung.shealth.vitality_score`
- Total rows (approx.): **431** · Columns: **69** · Separator: `,` · Encoding: `utf-8-sig` · Sample analyzed: 431 rows

| Column | Inferred type | Nulls (sample) | Examples |
| --- | --- | --- | --- |
| activity_level | integer | 0 | `-1`, `180004`, `180003` |
| activity_score | floating | 0 | `98.660995`, `45.265663`, `18.790558` |
| create_sh_ver | integer | 0 | `62850050`, `62900750`, `62920010` |
| active_time_scale | floating | 0 | `94.287384`, `42.51072`, `58.4908` |
| activity_balance_short_term_activity | floating | 78 | `11.041281`, `9.561079`, `11.62837` |
| activity_balance_long_term_activity | floating | 78 | `9.400625`, `9.237527`, `9.879502` |
| shr_balance_scale | floating | 0 | `75.48126`, `73.81254`, `69.34062` |
| mvpa_time_optimal_range_max | floating | 78 | `1772686.0`, `1726156.0`, `1981081.0` |
| mvpa_time_optimal_range_min | floating | 78 | `429614.0`, `401110.0`, `611833.0` |
| max_hr | floating | 0 | `196.0`, `202.0`, `201.0` |
| active_time | integer | 0 | `3268668`, `7989460`, `6363555` |
| shrv_balance_scale | floating | 0 | `72.75778`, `99.39795`, `98.206436` |
| main_sleep_wake_up_time | integer | 0 | `1736582940000`, `1736670570000`, `1736925960000` |
| mvpa_impulse_optimal_range_max | floating | 78 | `160.96628`, `160.70596`, `170.63869` |
| mvpa_impulse_optimal_range_min | floating | 78 | `118.59384`, `117.97522`, `125.299385` |
| shr_baseline_max | floating | 0 | `46.22872`, `46.265343`, `46.466236` |
| shr_baseline_min | floating | 0 | `43.795628`, `43.830326`, `44.02064` |
| shr_calculation_index | integer | 0 | `-1` |
| mvpa_time | integer | 0 | `1330010`, `915546`, `3388437` |
| skin_temperature_scale | floating | 431 | _(no data)_ |
| modify_sh_ver | integer | 0 | `62850050`, `62900750`, `62920010` |
| sleep_balance | floating | 0 | `0.50677633`, `0.47357038`, `0.42072684` |
| update_time | string | 0 | `2025-01-11 13:34:41.633`, `2025-01-12 14:02:31.627`, `2025-01-15 12:52:30.817` |
| create_time | string | 0 | `2025-01-11 13:34:41.633`, `2025-01-12 14:02:31.627`, `2025-01-15 12:52:30.817` |
| total_score | floating | 0 | `81.47289`, `75.318665`, `74.867966` |
| data_version | integer | 0 | `1`, `2`, `3` |
| avg_mid_sleep_time | floating | 0 | `4.5233335`, `4.5944443`, `4.43` |
| mvpa_time_range_max | floating | 78 | `7749361.0`, `7622611.0`, `8074237.0` |
| mvpa_time_range_min | floating | 78 | `0.0` |
| mvpa_impulse | floating | 0 | `131.82074`, `130.6002`, `134.65572` |
| shrv_calculation_index | integer | 0 | `-1` |
| sleep_regularity_scale | floating | 0 | `91.95712`, `91.7308`, `92.737595` |
| stable_hr_time_rate | floating | 0 | `0.41343668`, `0.56301534`, `0.8321168` |
| active_time_optimal_range_max | floating | 78 | `5784351.0`, `5685360.0`, `6148646.0` |
| active_time_optimal_range_min | floating | 78 | `3528202.0`, `3468354.0`, `3777565.0` |
| sleep_timing | floating | 0 | `1.7`, `1.4166666`, `0.5833333` |
| shr_score | floating | 0 | `75.48126`, `73.81254`, `69.34062` |
| shr_value | floating | 0 | `48.544716`, `48.89313`, `51.057323` |
| mvpa_impulse_scale | floating | 0 | `95.74126`, `94.77497`, `97.98569` |
| sleep_regularity | floating | 0 | `0.49627522`, `0.48013002`, `0.51805204` |
| sleep_timing_scale | floating | 0 | `88.0`, `90.83333`, `99.166664` |
| prev_shrv_avg | floating | 0 | `73.37227`, `135.12076`, `134.13504` |
| mvpa_time_scale | floating | 0 | `86.65485`, `99.51754`, `41.628845` |
| deviceuuid | string | 0 | `1kGlEKqwGK` |
| sleep_score | floating | 0 | `83.10998`, `85.48818`, `89.818924` |
| sleep_duration_scale | floating | 0 | `83.03333`, `83.48611`, `82.683334` |
| activity_balance | floating | 78 | `1.1745262`, `1.0350258`, `1.1770198` |
| activity_balance_range_max | floating | 78 | `2.65` |
| activity_balance_range_min | floating | 78 | `0.0` |
| mvpa_impulse_range_max | floating | 78 | `220.0`, `-1.0`, `198.81372` |
| mvpa_impulse_range_min | floating | 78 | `105.03999`, `0.0`, `104.52` |
| pkg_name | string | 0 | `com.sec.android.app.shealth` |
| sleep_balance_scale | floating | 0 | `92.10434`, `91.63883`, `94.10197` |
| shrv_score | floating | 0 | `72.75778`, `99.39795`, `98.206436` |
| shrv_value | floating | 0 | `135.78764`, `134.45721`, `132.18506` |
| sleep_duration | integer | 0 | `24492000`, `24655000`, `24366000` |
| skin_temperature_optimal_range_max | floating | 431 | _(no data)_ |
| skin_temperature_optimal_range_min | floating | 431 | _(no data)_ |
| activity_balance_scale | floating | 78 | `84.52843`, `96.84768`, `84.37881` |
| active_time_range_max | floating | 78 | `15824221.0`, `15551040.0`, `16699954.0` |
| active_time_range_min | floating | 78 | `0.0` |
| shrv_baseline_max | floating | 0 | `97.70139`, `187.40036`, `185.94244` |
| shrv_baseline_min | floating | 0 | `65.90126`, `119.523735`, `118.67352` |
| datauuid | string | 0 | `6ca2ff9a-096f-4329-a6fb-8b9bcf2b3c1a`, `94eaee33-2d3b-4832-a598-8c855997f0ef`, `911d67fe-2abb-4edb-9e5e-cd031dedcb74` |
| prev_shr_avg | floating | 0 | `48.66181`, `48.700363`, `48.911827` |
| day_time | string | 0 | `2025-01-11 00:00:00.000`, `2025-01-12 00:00:00.000`, `2025-01-15 00:00:00.000` |
| shrv_penalty | integer | 0 | `0` |
| activity_balance_optimal_range_max | floating | 78 | `1.1666666` |
| activity_balance_optimal_range_min | floating | 78 | `0.8333333` |

---
