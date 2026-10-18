# MISC case and readiness index

Source baseline `7e25ac2`; refinement baseline `c8bbc4e`.
These statuses describe proposed designs, not executed tests or policy approval.
All READY cases still need the ordinary [shared harness](../../../docs/testing/fixture-contract.md).

| Primary status | Cases |
| --- | ---: |
| READY | 80 |
| NEEDS_FIX | 2 |
| POLICY_BLOCKED | 20 |
| INFRA_BLOCKED | 1 |
| Total | 103 |

## Independently named cases

| New ID | test_name | Primary status | Design |
| --- | --- | --- | --- |
| MISC-T01a | `test_dashboard_selects_only_active_announcements` | READY | [case](cases/announcements.md#misc-t01a) |
| MISC-T01b | `test_next_dashboard_read_reflects_activation_change` | READY | [case](cases/announcements.md#misc-t01b) |
| MISC-T01c | `test_announcement_order_requires_product_rule` | POLICY_BLOCKED | [case](cases/announcements.md#misc-t01c) |
| MISC-T02a | `test_dashboard_empty_or_inactive_only_has_no_table` | READY | [case](cases/announcements.md#misc-t02a) |
| MISC-T03a | `test_announcement_create_defaults_and_string` | READY | [case](cases/announcements.md#misc-t03a) |
| MISC-T03b | `test_announcement_update_changes_only_update_timestamp` | READY | [case](cases/announcements.md#misc-t03b) |
| MISC-T03c | `test_unchanged_announcement_save_advances_updated_at` | READY | [case](cases/announcements.md#misc-t03c) |
| MISC-T04a | `test_announcement_full_clean_rejects_missing_or_long_title` | READY | [case](cases/announcements.md#misc-t04a) |
| MISC-T04b | `test_announcement_full_clean_accepts_maximum_title` | READY | [case](cases/announcements.md#misc-t04b) |
| MISC-T04c | `test_future_announcement_write_validation_needs_boundary` | POLICY_BLOCKED | [case](cases/announcements.md#misc-t04c) |
| MISC-T05a | `test_dst_model_default_optional_name_and_string` | READY | [case](cases/alerts.md#misc-t05a) |
| MISC-T05b | `test_dst_model_update_keeps_other_settings` | READY | [case](cases/alerts.md#misc-t05b) |
| MISC-T05c | `test_dst_model_full_clean_rejects_long_name` | READY | [case](cases/alerts.md#misc-t05c) |
| MISC-T06a | `test_tag_without_setting_shows_spring_message` | READY | [case](cases/alerts.md#misc-t06a) |
| MISC-T06b | `test_tag_without_setting_shows_fall_message` | READY | [case](cases/alerts.md#misc-t06b) |
| MISC-T06c | `test_blank_override_preserves_computed_message` | READY | [case](cases/alerts.md#misc-t06c) |
| MISC-T07a | `test_active_override_replaces_message_and_newlines` | READY | [case](cases/alerts.md#misc-t07a) |
| MISC-T07b | `test_inactive_setting_hides_dst_fragment` | READY | [case](cases/alerts.md#misc-t07b) |
| MISC-T07c | `test_explicit_reactivation_appears_on_next_read` | READY | [case](cases/alerts.md#misc-t07c) |
| MISC-T08a | `test_multi_setting_selection_needs_singleton_policy` | POLICY_BLOCKED | [case](cases/alerts.md#misc-t08a) |
| MISC-T08b | `test_setting_delete_fallback_needs_visibility_policy` | POLICY_BLOCKED | [case](cases/alerts.md#misc-t08b) |
| MISC-T09a | `test_announcement_template_escapes_untrusted_text` | READY | [case](cases/announcements.md#misc-t09a) |
| MISC-T09b | `test_announcement_template_prefers_updated_date` | READY | [case](cases/announcements.md#misc-t09b) |
| MISC-T09c | `test_announcement_template_created_date_fallback` | READY | [case](cases/announcements.md#misc-t09c) |
| MISC-T09d | `test_announcement_fragment_without_context_is_empty` | READY | [case](cases/announcements.md#misc-t09d) |
| MISC-T10a | `test_override_content_cannot_create_executable_markup` | NEEDS_FIX | [case](cases/alerts.md#misc-t10a) |
| MISC-T10b | `test_override_harmless_markup_needs_presentation_policy` | POLICY_BLOCKED | [case](cases/alerts.md#misc-t10b) |
| MISC-T11a | `test_fragment_controls_have_local_targets` | READY | [case](cases/alerts.md#misc-t11a) |
| MISC-T11b | `test_browser_dismissal_has_no_persistent_effect` | INFRA_BLOCKED | [case](cases/alerts.md#misc-t11b) |
| MISC-T12a | `test_spring_boundary_returns_strictly_future_calendar_date` | READY | [case](cases/calendar-failures.md#misc-t12a) |
| MISC-T12b | `test_spring_returned_wall_label_needs_normalization_policy` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t12b) |
| MISC-T13a | `test_fall_returned_transition_matches_physical_rollback` | NEEDS_FIX | [case](cases/calendar-failures.md#misc-t13a) |
| MISC-T13b | `test_fall_exact_and_after_boundary_need_strictness_decision` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t13b) |
| MISC-T14a | `test_fall_candidate_boundary_must_not_become_physical_contract` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t14a) |
| MISC-T15a | `test_year_rollover_keeps_next_spring_date` | READY | [case](cases/calendar-failures.md#misc-t15a) |
| MISC-T15b | `test_second_and_first_sunday_dates_across_years` | READY | [case](cases/calendar-failures.md#misc-t15b) |
| MISC-T15c | `test_chicago_calendar_is_independent_of_django_timezone` | READY | [case](cases/calendar-failures.md#misc-t15c) |
| MISC-T16a | `test_tag_none_result_uses_unavailable_message` | READY | [case](cases/calendar-failures.md#misc-t16a) |
| MISC-T16b | `test_tag_none_result_still_allows_setting_override` | READY | [case](cases/calendar-failures.md#misc-t16b) |
| MISC-T16c | `test_clock_or_timezone_failure_needs_error_policy` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t16c) |
| MISC-T16d | `test_tag_dependency_exception_needs_fallback_policy` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t16d) |
| MISC-T16e | `test_setting_lookup_failure_needs_database_error_policy` | POLICY_BLOCKED | [case](cases/calendar-failures.md#misc-t16e) |
| MISC-T16f | `test_injected_does_not_exist_keeps_tag_default` | READY | [case](cases/calendar-failures.md#misc-t16f) |
| MISC-T17a | `test_resolver_contains_no_misc_view` | READY | [case](cases/integration.md#misc-t17a) |
| MISC-T17b | `test_direct_view_context_messages_without_public_endpoint` | READY | [case](cases/integration.md#misc-t17b) |
| MISC-T17c | `test_unused_view_lifecycle_needs_decision` | POLICY_BLOCKED | [case](cases/integration.md#misc-t17c) |
| MISC-T18a | `test_eligible_roles_receive_global_active_content` | READY | [case](cases/integration.md#misc-t18a) |
| MISC-T19a | `test_anonymous_dashboard_redirect_discloses_no_fragment` | READY | [case](cases/integration.md#misc-t19a) |
| MISC-T19b | `test_any_new_member_combination_redirects_before_alert_render` | READY | [case](cases/integration.md#misc-t19b) |
| MISC-T20a | `test_missing_profile_dashboard_needs_response_policy` | POLICY_BLOCKED | [case](cases/integration.md#misc-t20a) |
| MISC-T20b | `test_home_has_no_announcement_or_clock_integration` | READY | [case](cases/integration.md#misc-t20b) |
| MISC-T21a | `test_anonymous_nonstaff_and_inactive_staff_cannot_enter_admin` | READY | [case](cases/admin-permissions.md#misc-t21a) |
| MISC-T21b | `test_staff_without_view_or_change_cannot_list_models` | READY | [case](cases/admin-permissions.md#misc-t21b) |
| MISC-T21c | `test_view_permission_allows_read_without_writes` | READY | [case](cases/admin-permissions.md#misc-t21c) |
| MISC-T21d | `test_add_permission_is_required_for_direct_add_post` | READY | [case](cases/admin-permissions.md#misc-t21d) |
| MISC-T21e | `test_change_permission_is_required_for_direct_edit_post` | READY | [case](cases/admin-permissions.md#misc-t21e) |
| MISC-T21f | `test_delete_permission_is_required_for_detail_delete` | READY | [case](cases/admin-permissions.md#misc-t21f) |
| MISC-T21g | `test_hidden_bulk_delete_cannot_bypass_delete_permission` | READY | [case](cases/admin-permissions.md#misc-t21g) |
| MISC-T21h | `test_permissions_are_isolated_by_model` | READY | [case](cases/admin-permissions.md#misc-t21h) |
| MISC-T21i | `test_chapter_role_and_record_creator_do_not_restrict_admin_read` | READY | [case](cases/admin-permissions.md#misc-t21i) |
| MISC-T21j | `test_delete_only_permission_does_not_grant_changelist` | READY | [case](cases/admin-permissions.md#misc-t21j) |
| MISC-T21k | `test_synthetic_superuser_can_read_both_models` | READY | [case](cases/admin-permissions.md#misc-t21k) |
| MISC-T21l | `test_admin_does_not_require_member_profile` | READY | [case](cases/admin-permissions.md#misc-t21l) |
| MISC-T22a | `test_announcement_admin_exposes_only_title_and_content` | READY | [case](cases/admin-writes.md#misc-t22a) |
| MISC-T22b | `test_announcement_admin_add_sets_defaults_and_add_log` | READY | [case](cases/admin-writes.md#misc-t22b) |
| MISC-T22c | `test_announcement_admin_edit_preserves_inactive_flag` | READY | [case](cases/admin-writes.md#misc-t22c) |
| MISC-T22d | `test_announcement_admin_ignores_excluded_field_payloads` | READY | [case](cases/admin-writes.md#misc-t22d) |
| MISC-T22e | `test_save_continue_and_addanother_have_concrete_redirects` | READY | [case](cases/admin-writes.md#misc-t22e) |
| MISC-T22f | `test_saveasnew_requires_add_permission_even_when_button_hidden` | READY | [case](cases/admin-writes.md#misc-t22f) |
| MISC-T22g | `test_authorized_saveasnew_creates_separate_announcement` | READY | [case](cases/admin-writes.md#misc-t22g) |
| MISC-T22h | `test_announcement_activation_ui_needs_product_decision` | POLICY_BLOCKED | [case](cases/admin-writes.md#misc-t22h) |
| MISC-T22i | `test_add_only_staff_can_create_without_list_permission` | READY | [case](cases/admin-writes.md#misc-t22i) |
| MISC-T22j | `test_announcement_add_flags_redirect_without_extra_inserts` | READY | [case](cases/admin-writes.md#misc-t22j) |
| MISC-T23a | `test_dst_admin_form_and_list_expose_name_and_active` | READY | [case](cases/admin-writes.md#misc-t23a) |
| MISC-T23b | `test_dst_admin_add_records_active_name_and_log` | READY | [case](cases/admin-writes.md#misc-t23b) |
| MISC-T23c | `test_dst_admin_edit_omitted_checkbox_disables_setting` | READY | [case](cases/admin-writes.md#misc-t23c) |
| MISC-T23d | `test_dst_admin_name_normalization_accepts_blank_values` | READY | [case](cases/admin-writes.md#misc-t23d) |
| MISC-T23e | `test_repeated_dst_edit_does_not_insert_duplicate` | READY | [case](cases/admin-writes.md#misc-t23e) |
| MISC-T23f | `test_dst_admin_save_flags_and_saveasnew_action` | READY | [case](cases/admin-writes.md#misc-t23f) |
| MISC-T23g | `test_dst_add_flags_redirect_without_extra_inserts` | READY | [case](cases/admin-writes.md#misc-t23g) |
| MISC-T24a | `test_admin_invalid_fields_return_errors_without_writes` | READY | [case](cases/admin-writes.md#misc-t24a) |
| MISC-T24b | `test_missing_and_malformed_admin_object_ids_do_not_mutate` | READY | [case](cases/admin-writes.md#misc-t24b) |
| MISC-T24c | `test_unknown_or_empty_bulk_action_has_no_state_effect` | READY | [case](cases/admin-writes.md#misc-t24c) |
| MISC-T25a | `test_admin_mutations_reject_missing_or_bad_csrf_token` | READY | [case](cases/admin-audit-failures.md#misc-t25a) |
| MISC-T25b | `test_admin_valid_csrf_pair_allows_intended_write` | READY | [case](cases/admin-audit-failures.md#misc-t25b) |
| MISC-T25c | `test_demo_boundary_blocks_model_admin_even_with_permission` | READY | [case](cases/admin-audit-failures.md#misc-t25c) |
| MISC-T26a | `test_detail_delete_confirmation_get_is_read_only` | READY | [case](cases/admin-audit-failures.md#misc-t26a) |
| MISC-T26b | `test_detail_delete_removes_only_target_and_logs_once` | READY | [case](cases/admin-audit-failures.md#misc-t26b) |
| MISC-T26c | `test_bulk_delete_confirmation_preserves_selected_rows` | READY | [case](cases/admin-audit-failures.md#misc-t26c) |
| MISC-T26d | `test_confirmed_bulk_delete_keeps_unselected_records` | READY | [case](cases/admin-audit-failures.md#misc-t26d) |
| MISC-T26e | `test_repeated_stale_delete_is_non_mutating` | READY | [case](cases/admin-audit-failures.md#misc-t26e) |
| MISC-T26f | `test_last_setting_delete_requires_product_visibility_choice` | POLICY_BLOCKED | [case](cases/admin-audit-failures.md#misc-t26f) |
| MISC-T27a | `test_admin_save_log_failure_rolls_back_model_write` | READY | [case](cases/admin-audit-failures.md#misc-t27a) |
| MISC-T27b | `test_admin_model_save_failure_creates_no_audit_entry` | READY | [case](cases/admin-audit-failures.md#misc-t27b) |
| MISC-T27c | `test_detail_delete_failure_rolls_back_preceding_delete_log` | READY | [case](cases/admin-audit-failures.md#misc-t27c) |
| MISC-T27d | `test_bulk_delete_failure_audit_contract_needs_decision` | POLICY_BLOCKED | [case](cases/admin-audit-failures.md#misc-t27d) |
| MISC-T28a | `test_stale_admin_write_requires_conflict_policy` | POLICY_BLOCKED | [case](cases/admin-audit-failures.md#misc-t28a) |
| MISC-T28b | `test_concurrent_admin_write_requires_policy_and_postgresql` | POLICY_BLOCKED | [case](cases/admin-audit-failures.md#misc-t28b) |
| MISC-T29a | `test_admin_history_is_scoped_to_object_and_actor` | READY | [case](cases/admin-audit-failures.md#misc-t29a) |
| MISC-T29b | `test_admin_history_denies_staff_without_view_or_change` | READY | [case](cases/admin-audit-failures.md#misc-t29b) |
| MISC-T29c | `test_orm_and_reader_actions_do_not_create_admin_logs` | READY | [case](cases/admin-audit-failures.md#misc-t29c) |
| MISC-T29d | `test_business_audit_retention_requires_shared_policy` | POLICY_BLOCKED | [case](cases/admin-audit-failures.md#misc-t29d) |
| MISC-T30a | `test_dashboard_read_failure_requires_fragment_isolation_rule` | POLICY_BLOCKED | [case](cases/integration.md#misc-t30a) |

## Original group preservation

Every original group is retained as a parent; suffixes identify independent designs.
The old bundled case prose is replaced, not retained as a second specification.

| Original ID | New IDs |
| --- | --- |
| MISC-T01 | [MISC-T01a](cases/announcements.md#misc-t01a), [MISC-T01b](cases/announcements.md#misc-t01b), [MISC-T01c](cases/announcements.md#misc-t01c) |
| MISC-T02 | [MISC-T02a](cases/announcements.md#misc-t02a) |
| MISC-T03 | [MISC-T03a](cases/announcements.md#misc-t03a), [MISC-T03b](cases/announcements.md#misc-t03b), [MISC-T03c](cases/announcements.md#misc-t03c) |
| MISC-T04 | [MISC-T04a](cases/announcements.md#misc-t04a), [MISC-T04b](cases/announcements.md#misc-t04b), [MISC-T04c](cases/announcements.md#misc-t04c) |
| MISC-T05 | [MISC-T05a](cases/alerts.md#misc-t05a), [MISC-T05b](cases/alerts.md#misc-t05b), [MISC-T05c](cases/alerts.md#misc-t05c) |
| MISC-T06 | [MISC-T06a](cases/alerts.md#misc-t06a), [MISC-T06b](cases/alerts.md#misc-t06b), [MISC-T06c](cases/alerts.md#misc-t06c) |
| MISC-T07 | [MISC-T07a](cases/alerts.md#misc-t07a), [MISC-T07b](cases/alerts.md#misc-t07b), [MISC-T07c](cases/alerts.md#misc-t07c) |
| MISC-T08 | [MISC-T08a](cases/alerts.md#misc-t08a), [MISC-T08b](cases/alerts.md#misc-t08b) |
| MISC-T09 | [MISC-T09a](cases/announcements.md#misc-t09a), [MISC-T09b](cases/announcements.md#misc-t09b), [MISC-T09c](cases/announcements.md#misc-t09c), [MISC-T09d](cases/announcements.md#misc-t09d) |
| MISC-T10 | [MISC-T10a](cases/alerts.md#misc-t10a), [MISC-T10b](cases/alerts.md#misc-t10b) |
| MISC-T11 | [MISC-T11a](cases/alerts.md#misc-t11a), [MISC-T11b](cases/alerts.md#misc-t11b) |
| MISC-T12 | [MISC-T12a](cases/calendar-failures.md#misc-t12a), [MISC-T12b](cases/calendar-failures.md#misc-t12b) |
| MISC-T13 | [MISC-T13a](cases/calendar-failures.md#misc-t13a), [MISC-T13b](cases/calendar-failures.md#misc-t13b) |
| MISC-T14 | [MISC-T14a](cases/calendar-failures.md#misc-t14a) |
| MISC-T15 | [MISC-T15a](cases/calendar-failures.md#misc-t15a), [MISC-T15b](cases/calendar-failures.md#misc-t15b), [MISC-T15c](cases/calendar-failures.md#misc-t15c) |
| MISC-T16 | [MISC-T16a](cases/calendar-failures.md#misc-t16a), [MISC-T16b](cases/calendar-failures.md#misc-t16b), [MISC-T16c](cases/calendar-failures.md#misc-t16c), [MISC-T16d](cases/calendar-failures.md#misc-t16d), [MISC-T16e](cases/calendar-failures.md#misc-t16e), [MISC-T16f](cases/calendar-failures.md#misc-t16f) |
| MISC-T17 | [MISC-T17a](cases/integration.md#misc-t17a), [MISC-T17b](cases/integration.md#misc-t17b), [MISC-T17c](cases/integration.md#misc-t17c) |
| MISC-T18 | [MISC-T18a](cases/integration.md#misc-t18a) |
| MISC-T19 | [MISC-T19a](cases/integration.md#misc-t19a), [MISC-T19b](cases/integration.md#misc-t19b) |
| MISC-T20 | [MISC-T20a](cases/integration.md#misc-t20a), [MISC-T20b](cases/integration.md#misc-t20b) |
| MISC-T21 | [MISC-T21a](cases/admin-permissions.md#misc-t21a), [MISC-T21b](cases/admin-permissions.md#misc-t21b), [MISC-T21c](cases/admin-permissions.md#misc-t21c), [MISC-T21d](cases/admin-permissions.md#misc-t21d), [MISC-T21e](cases/admin-permissions.md#misc-t21e), [MISC-T21f](cases/admin-permissions.md#misc-t21f), [MISC-T21g](cases/admin-permissions.md#misc-t21g), [MISC-T21h](cases/admin-permissions.md#misc-t21h), [MISC-T21i](cases/admin-permissions.md#misc-t21i), [MISC-T21j](cases/admin-permissions.md#misc-t21j), [MISC-T21k](cases/admin-permissions.md#misc-t21k), [MISC-T21l](cases/admin-permissions.md#misc-t21l) |
| MISC-T22 | [MISC-T22a](cases/admin-writes.md#misc-t22a), [MISC-T22b](cases/admin-writes.md#misc-t22b), [MISC-T22c](cases/admin-writes.md#misc-t22c), [MISC-T22d](cases/admin-writes.md#misc-t22d), [MISC-T22e](cases/admin-writes.md#misc-t22e), [MISC-T22f](cases/admin-writes.md#misc-t22f), [MISC-T22g](cases/admin-writes.md#misc-t22g), [MISC-T22h](cases/admin-writes.md#misc-t22h), [MISC-T22i](cases/admin-writes.md#misc-t22i), [MISC-T22j](cases/admin-writes.md#misc-t22j) |
| MISC-T23 | [MISC-T23a](cases/admin-writes.md#misc-t23a), [MISC-T23b](cases/admin-writes.md#misc-t23b), [MISC-T23c](cases/admin-writes.md#misc-t23c), [MISC-T23d](cases/admin-writes.md#misc-t23d), [MISC-T23e](cases/admin-writes.md#misc-t23e), [MISC-T23f](cases/admin-writes.md#misc-t23f), [MISC-T23g](cases/admin-writes.md#misc-t23g) |
| MISC-T24 | [MISC-T24a](cases/admin-writes.md#misc-t24a), [MISC-T24b](cases/admin-writes.md#misc-t24b), [MISC-T24c](cases/admin-writes.md#misc-t24c) |
| MISC-T25 | [MISC-T25a](cases/admin-audit-failures.md#misc-t25a), [MISC-T25b](cases/admin-audit-failures.md#misc-t25b), [MISC-T25c](cases/admin-audit-failures.md#misc-t25c) |
| MISC-T26 | [MISC-T26a](cases/admin-audit-failures.md#misc-t26a), [MISC-T26b](cases/admin-audit-failures.md#misc-t26b), [MISC-T26c](cases/admin-audit-failures.md#misc-t26c), [MISC-T26d](cases/admin-audit-failures.md#misc-t26d), [MISC-T26e](cases/admin-audit-failures.md#misc-t26e), [MISC-T26f](cases/admin-audit-failures.md#misc-t26f) |
| MISC-T27 | [MISC-T27a](cases/admin-audit-failures.md#misc-t27a), [MISC-T27b](cases/admin-audit-failures.md#misc-t27b), [MISC-T27c](cases/admin-audit-failures.md#misc-t27c), [MISC-T27d](cases/admin-audit-failures.md#misc-t27d) |
| MISC-T28 | [MISC-T28a](cases/admin-audit-failures.md#misc-t28a), [MISC-T28b](cases/admin-audit-failures.md#misc-t28b) |
| MISC-T29 | [MISC-T29a](cases/admin-audit-failures.md#misc-t29a), [MISC-T29b](cases/admin-audit-failures.md#misc-t29b), [MISC-T29c](cases/admin-audit-failures.md#misc-t29c), [MISC-T29d](cases/admin-audit-failures.md#misc-t29d) |
| MISC-T30 | [MISC-T30a](cases/integration.md#misc-t30a) |

## Operation completeness

| Operation | New case IDs |
| --- | --- |
| MISC-O01 | MISC-T01a, MISC-T01b, MISC-T01c, MISC-T02a, MISC-T30a |
| MISC-O02 | MISC-T06a, MISC-T06b, MISC-T06c, MISC-T07a, MISC-T07c, MISC-T08a, MISC-T08b, MISC-T16a, MISC-T16b, MISC-T16d, MISC-T16e, MISC-T16f |
| MISC-O03 | MISC-T12a, MISC-T12b, MISC-T13a, MISC-T13b, MISC-T14a, MISC-T15a, MISC-T15b, MISC-T15c, MISC-T16c |
| MISC-O04 | MISC-T09a, MISC-T09b, MISC-T09c, MISC-T09d |
| MISC-O05 | MISC-T07b, MISC-T10a, MISC-T10b, MISC-T11a, MISC-T11b |
| MISC-O06 | MISC-T17b, MISC-T17c |
| MISC-O07 | MISC-T03a, MISC-T03b, MISC-T03c, MISC-T04a, MISC-T04b, MISC-T04c, MISC-T29c |
| MISC-O08 | MISC-T05a, MISC-T05b, MISC-T05c |
| MISC-O09 | MISC-T21a, MISC-T21b, MISC-T21c, MISC-T21d, MISC-T21e, MISC-T21i, MISC-T21k, MISC-T21l, MISC-T22a, MISC-T22b, MISC-T22c, MISC-T22d, MISC-T22e, MISC-T22f, MISC-T22g, MISC-T22h, MISC-T22i, MISC-T22j, MISC-T24a, MISC-T24b, MISC-T25a, MISC-T25b, MISC-T25c, MISC-T27a, MISC-T27b, MISC-T29a, MISC-T29b, MISC-T29d |
| MISC-O10 | MISC-T21h, MISC-T23a, MISC-T23b, MISC-T23c, MISC-T23d, MISC-T23e, MISC-T23f, MISC-T23g, MISC-T28a, MISC-T28b |
| MISC-O11 | MISC-T21f, MISC-T21g, MISC-T21j, MISC-T24c, MISC-T26a, MISC-T26b, MISC-T26c, MISC-T26d, MISC-T26e, MISC-T26f, MISC-T27c, MISC-T27d |
| MISC-O12 | MISC-T17a, MISC-T18a, MISC-T19a, MISC-T19b, MISC-T20a, MISC-T20b |
