# Atomic case index and Wave 1 traceability

Source baseline: `7e25ac2f06b2d88a0220526771585f30df10c57a`.
Documentation refinement baseline: `c8bbc4e`.

33 original groups map to 118 independently named designs. Parameter values
inside a case are variants, not additional counted cases. These are design counts,
not executed tests or coverage measurements.

| Primary status | Count |
| --- | ---: |
| READY | 66 |
| NEEDS_FIX | 11 |
| POLICY_BLOCKED | 41 |
| INFRA_BLOCKED | 0 |
| Total | 118 |

READY means expected-current preservation after the shared harness exists.
NEEDS_FIX names a specific unsafe invariant; POLICY_BLOCKED has no invented outcome.
The ordinary shared harness is never counted as a special infrastructure blocker.
Race cases list PostgreSQL facilities but are primarily blocked by Q4/Q8 policy.

## Case index

| New ID | test_name | Primary status | Case file/anchor |
| --- | --- | --- | --- |
| PH-C01a | `test_anonymous_domain_requests_require_login` | READY | [access](cases/access.md#ph-c01a--test_anonymous_domain_requests_require_login) |
| PH-C01b | `test_non_active_actors_cannot_submit_or_read_member_pages` | READY | [access](cases/access.md#ph-c01b--test_non_active_actors_cannot_submit_or_read_member_pages) |
| PH-C01c | `test_approval_requires_both_narrow_roles` | READY | [access](cases/access.md#ph-c01c--test_approval_requires_both_narrow_roles) |
| PH-C01d | `test_non_chairs_cannot_read_or_post_edit` | READY | [access](cases/access.md#ph-c01d--test_non_chairs_cannot_read_or_post_edit) |
| PH-C01e | `test_missing_profiles_are_denied_by_role_decorators` | READY | [access](cases/access.md#ph-c01e--test_missing_profiles_are_denied_by_role_decorators) |
| PH-C01f | `test_chair_without_active_edit_authority_needs_policy` | POLICY_BLOCKED | [access](cases/access.md#ph-c01f--test_chair_without_active_edit_authority_needs_policy) |
| PH-C02a | `test_submit_csrf_rejects_absent_or_bad_token` | READY | [access](cases/access.md#ph-c02a--test_submit_csrf_rejects_absent_or_bad_token) |
| PH-C02b | `test_approve_csrf_rejects_absent_or_bad_token` | READY | [access](cases/access.md#ph-c02b--test_approve_csrf_rejects_absent_or_bad_token) |
| PH-C02c | `test_deny_csrf_rejects_absent_or_bad_token` | READY | [access](cases/access.md#ph-c02c--test_deny_csrf_rejects_absent_or_bad_token) |
| PH-C02d | `test_edit_csrf_rejects_absent_or_bad_token` | READY | [access](cases/access.md#ph-c02d--test_edit_csrf_rejects_absent_or_bad_token) |
| PH-C03a | `test_mutation_route_other_methods_need_policy` | POLICY_BLOCKED | [access](cases/access.md#ph-c03a--test_mutation_route_other_methods_need_policy) |
| PH-C03b | `test_read_route_post_methods_need_policy` | POLICY_BLOCKED | [access](cases/access.md#ph-c03b--test_read_route_post_methods_need_policy) |
| PH-C03c | `test_role_denial_uses_poll_without_referrer` | READY | [access](cases/access.md#ph-c03c--test_role_denial_uses_poll_without_referrer) |
| PH-C03d | `test_role_denial_uses_safe_referrer` | READY | [access](cases/access.md#ph-c03d--test_role_denial_uses_safe_referrer) |
| PH-C03e | `test_role_denial_rejects_external_referrer` | NEEDS_FIX | [access](cases/access.md#ph-c03e--test_role_denial_rejects_external_referrer) |
| PH-C04a | `test_submission_form_exposes_three_fields` | READY | [submissions](cases/submissions.md#ph-c04a--test_submission_form_exposes_three_fields) |
| PH-C04b | `test_integer_submission_persists_exact_values` | READY | [submissions](cases/submissions.md#ph-c04b--test_integer_submission_persists_exact_values) |
| PH-C04c | `test_submitted_owner_status_and_audit_are_ignored` | READY | [submissions](cases/submissions.md#ph-c04c--test_submitted_owner_status_and_audit_are_ignored) |
| PH-C05a | `test_submission_rejects_below_minimum_hours` | READY | [submissions](cases/submissions.md#ph-c05a--test_submission_rejects_below_minimum_hours) |
| PH-C05b | `test_integral_float_string_preserves_integer_hours` | READY | [submissions](cases/submissions.md#ph-c05b--test_integral_float_string_preserves_integer_hours) |
| PH-C05c | `test_fractional_submission_requires_precision_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c05c--test_fractional_submission_requires_precision_policy) |
| PH-C05d | `test_edit_minimum_and_fractional_hours_require_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c05d--test_edit_minimum_and_fractional_hours_require_policy) |
| PH-C06a | `test_submission_parse_errors_leave_no_event` | READY | [submissions](cases/submissions.md#ph-c06a--test_submission_parse_errors_leave_no_event) |
| PH-C06b | `test_submission_nonfinite_hours_create_no_record` | READY | [submissions](cases/submissions.md#ph-c06b--test_submission_nonfinite_hours_create_no_record) |
| PH-C06c | `test_edit_invalid_hours_returns_controlled_error` | NEEDS_FIX | [submissions](cases/submissions.md#ph-c06c--test_edit_invalid_hours_returns_controlled_error) |
| PH-C06d | `test_huge_finite_hours_need_upper_bound` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c06d--test_huge_finite_hours_need_upper_bound) |
| PH-C07a | `test_missing_submission_keys_and_bad_dates_do_not_write` | READY | [submissions](cases/submissions.md#ph-c07a--test_missing_submission_keys_and_bad_dates_do_not_write) |
| PH-C07b | `test_empty_and_overlong_titles_require_validation_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c07b--test_empty_and_overlong_titles_require_validation_policy) |
| PH-C07c | `test_hundred_character_title_round_trips` | READY | [submissions](cases/submissions.md#ph-c07c--test_hundred_character_title_round_trips) |
| PH-C07d | `test_unicode_and_html_title_render_as_text` | READY | [submissions](cases/submissions.md#ph-c07d--test_unicode_and_html_title_render_as_text) |
| PH-C07e | `test_past_and_future_event_dates_need_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c07e--test_past_and_future_event_dates_need_policy) |
| PH-C08a | `test_submit_prewrite_save_failure_is_reported_without_row` | READY | [submissions](cases/submissions.md#ph-c08a--test_submit_prewrite_save_failure_is_reported_without_row) |
| PH-C08b | `test_identical_submit_retry_requires_idempotency_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c08b--test_identical_submit_retry_requires_idempotency_policy) |
| PH-C08c | `test_submit_postwrite_exception_needs_commit_policy` | POLICY_BLOCKED | [submissions](cases/submissions.md#ph-c08c--test_submit_postwrite_exception_needs_commit_policy) |
| PH-C08d | `test_submission_does_not_disclose_save_exception_details` | NEEDS_FIX | [submissions](cases/submissions.md#ph-c08d--test_submission_does_not_disclose_save_exception_details) |
| PH-C09a | `test_pending_list_contains_only_requested_rows_by_date` | READY | [approvals](cases/approvals.md#ph-c09a--test_pending_list_contains_only_requested_rows_by_date) |
| PH-C09b | `test_initial_approval_updates_only_decision_fields` | READY | [approvals](cases/approvals.md#ph-c09b--test_initial_approval_updates_only_decision_fields) |
| PH-C10a | `test_initial_denial_updates_only_decision_fields` | READY | [approvals](cases/approvals.md#ph-c10a--test_initial_denial_updates_only_decision_fields) |
| PH-C10b | `test_denied_event_remains_personal_but_not_approved_history` | READY | [approvals](cases/approvals.md#ph-c10b--test_denied_event_remains_personal_but_not_approved_history) |
| PH-C11a | `test_bad_decision_event_ids_report_error_without_write` | READY | [approvals](cases/approvals.md#ph-c11a--test_bad_decision_event_ids_report_error_without_write) |
| PH-C11b | `test_unknown_decision_action_cannot_report_success` | NEEDS_FIX | [approvals](cases/approvals.md#ph-c11b--test_unknown_decision_action_cannot_report_success) |
| PH-C11c | `test_decision_helper_nonpost_is_noop` | READY | [approvals](cases/approvals.md#ph-c11c--test_decision_helper_nonpost_is_noop) |
| PH-C11d | `test_direct_decision_callable_needs_authorization_boundary` | NEEDS_FIX | [approvals](cases/approvals.md#ph-c11d--test_direct_decision_callable_needs_authorization_boundary) |
| PH-C12a | `test_approved_to_approve_requires_transition_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12a--test_approved_to_approve_requires_transition_policy) |
| PH-C12b | `test_denied_to_deny_requires_transition_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12b--test_denied_to_deny_requires_transition_policy) |
| PH-C12c | `test_approved_to_deny_requires_transition_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12c--test_approved_to_deny_requires_transition_policy) |
| PH-C12d | `test_denied_to_approve_requires_transition_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12d--test_denied_to_approve_requires_transition_policy) |
| PH-C12e | `test_self_approve_requires_review_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12e--test_self_approve_requires_review_policy) |
| PH-C12f | `test_self_deny_requires_review_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c12f--test_self_deny_requires_review_policy) |
| PH-C13a | `test_decision_prewrite_save_failure_preserves_request` | READY | [approvals](cases/approvals.md#ph-c13a--test_decision_prewrite_save_failure_preserves_request) |
| PH-C13b | `test_decision_postwrite_exception_needs_commit_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c13b--test_decision_postwrite_exception_needs_commit_policy) |
| PH-C13c | `test_competing_approve_and_deny_need_conflict_policy` | POLICY_BLOCKED | [approvals](cases/approvals.md#ph-c13c--test_competing_approve_and_deny_need_conflict_policy) |
| PH-C14a | `test_edit_get_populates_form_without_audit_write` | READY | [edits](cases/edits.md#ph-c14a--test_edit_get_populates_form_without_audit_write) |
| PH-C14b | `test_chair_edit_field_whitelist_needs_reapproval_policy` | POLICY_BLOCKED | [edits](cases/edits.md#ph-c14b--test_chair_edit_field_whitelist_needs_reapproval_policy) |
| PH-C14c | `test_second_edit_needs_latest_editor_and_audit_policy` | POLICY_BLOCKED | [edits](cases/edits.md#ph-c14c--test_second_edit_needs_latest_editor_and_audit_policy) |
| PH-C15a | `test_unknown_numeric_edit_target_is_404` | READY | [edits](cases/edits.md#ph-c15a--test_unknown_numeric_edit_target_is_404) |
| PH-C15b | `test_noninteger_edit_paths_do_not_resolve` | READY | [edits](cases/edits.md#ph-c15b--test_noninteger_edit_paths_do_not_resolve) |
| PH-C15c | `test_edit_missing_title_or_bad_date_is_controlled` | NEEDS_FIX | [edits](cases/edits.md#ph-c15c--test_edit_missing_title_or_bad_date_is_controlled) |
| PH-C16a | `test_edit_prewrite_failure_preserves_entire_target` | NEEDS_FIX | [edits](cases/edits.md#ph-c16a--test_edit_prewrite_failure_preserves_entire_target) |
| PH-C16b | `test_edit_postwrite_exception_needs_commit_policy` | POLICY_BLOCKED | [edits](cases/edits.md#ph-c16b--test_edit_postwrite_exception_needs_commit_policy) |
| PH-C16c | `test_stale_edit_and_approval_need_conflict_policy` | POLICY_BLOCKED | [edits](cases/edits.md#ph-c16c--test_stale_edit_and_approval_need_conflict_policy) |
| PH-C16d | `test_competing_edits_need_conflict_policy` | POLICY_BLOCKED | [edits](cases/edits.md#ph-c16d--test_competing_edits_need_conflict_policy) |
| PH-C17a | `test_academic_year_dates_are_july_through_june` | READY | [statistics](cases/statistics.md#ph-c17a--test_academic_year_dates_are_july_through_june) |
| PH-C17b | `test_available_years_before_and_after_july` | READY | [statistics](cases/statistics.md#ph-c17b--test_available_years_before_and_after_july) |
| PH-C17c | `test_available_year_count_can_be_zero_or_one` | READY | [statistics](cases/statistics.md#ph-c17c--test_available_year_count_can_be_zero_or_one) |
| PH-C17d | `test_dashboard_default_year_before_july` | READY | [statistics](cases/statistics.md#ph-c17d--test_dashboard_default_year_before_july) |
| PH-C17e | `test_dashboard_default_year_from_july` | READY | [statistics](cases/statistics.md#ph-c17e--test_dashboard_default_year_from_july) |
| PH-C17f | `test_explicit_dashboard_year_overrides_clock` | READY | [statistics](cases/statistics.md#ph-c17f--test_explicit_dashboard_year_overrides_clock) |
| PH-C17g | `test_date_helper_invalid_arguments_need_contract` | POLICY_BLOCKED | [statistics](cases/statistics.md#ph-c17g--test_date_helper_invalid_arguments_need_contract) |
| PH-C18a | `test_chapter_and_personal_approved_totals_are_scoped` | READY | [statistics](cases/statistics.md#ph-c18a--test_chapter_and_personal_approved_totals_are_scoped) |
| PH-C18b | `test_goal_threshold_is_ten_approved_hours` | READY | [statistics](cases/statistics.md#ph-c18b--test_goal_threshold_is_ten_approved_hours) |
| PH-C18c | `test_multiple_nonactive_roles_do_not_duplicate_statistics` | READY | [statistics](cases/statistics.md#ph-c18c--test_multiple_nonactive_roles_do_not_duplicate_statistics) |
| PH-C19a | `test_year_range_includes_july_first_and_june_thirtieth` | READY | [statistics](cases/statistics.md#ph-c19a--test_year_range_includes_july_first_and_june_thirtieth) |
| PH-C19b | `test_empty_selected_year_retains_zero_active_members` | READY | [statistics](cases/statistics.md#ph-c19b--test_empty_selected_year_retains_zero_active_members) |
| PH-C19c | `test_statistics_empty_profile_input_returns_zeroes` | READY | [statistics](cases/statistics.md#ph-c19c--test_statistics_empty_profile_input_returns_zeroes) |
| PH-C19d | `test_unwrapped_dashboard_zero_denominator_is_safe` | READY | [statistics](cases/statistics.md#ph-c19d--test_unwrapped_dashboard_zero_denominator_is_safe) |
| PH-C20a | `test_invalid_dashboard_year_is_a_controlled_error` | NEEDS_FIX | [statistics](cases/statistics.md#ph-c20a--test_invalid_dashboard_year_is_a_controlled_error) |
| PH-C20b | `test_historical_year_outside_dropdown_needs_range_policy` | POLICY_BLOCKED | [statistics](cases/statistics.md#ph-c20b--test_historical_year_outside_dropdown_needs_range_policy) |
| PH-C20c | `test_declared_chair_dashboard_flag_needs_canonical_role_policy` | POLICY_BLOCKED | [statistics](cases/statistics.md#ph-c20c--test_declared_chair_dashboard_flag_needs_canonical_role_policy) |
| PH-C20d | `test_undeclared_chair_role_cannot_gain_decision_permissions` | POLICY_BLOCKED | [statistics](cases/statistics.md#ph-c20d--test_undeclared_chair_role_cannot_gain_decision_permissions) |
| PH-C21a | `test_history_helper_buckets_approved_events_and_lifetime` | READY | [history-tags](cases/history-tags.md#ph-c21a--test_history_helper_buckets_approved_events_and_lifetime) |
| PH-C21b | `test_own_history_view_renders_approved_only` | READY | [history-tags](cases/history-tags.md#ph-c21b--test_own_history_view_renders_approved_only) |
| PH-C21c | `test_empty_approved_history_renders_zero_and_empty_text` | READY | [history-tags](cases/history-tags.md#ph-c21c--test_empty_approved_history_renders_zero_and_empty_text) |
| PH-C21d | `test_history_marks_edited_event` | READY | [history-tags](cases/history-tags.md#ph-c21d--test_history_marks_edited_event) |
| PH-C21e | `test_history_edit_link_tracks_declared_chair_role` | READY | [history-tags](cases/history-tags.md#ph-c21e--test_history_edit_link_tracks_declared_chair_role) |
| PH-C22a | `test_other_and_inactive_history_visibility_needs_policy` | POLICY_BLOCKED | [history-tags](cases/history-tags.md#ph-c22a--test_other_and_inactive_history_visibility_needs_policy) |
| PH-C22b | `test_missing_target_profile_redirects_without_record_changes` | READY | [history-tags](cases/history-tags.md#ph-c22b--test_missing_target_profile_redirects_without_record_changes) |
| PH-C23a | `test_hours_remaining_clamps_numeric_difference` | READY | [history-tags](cases/history-tags.md#ph-c23a--test_hours_remaining_clamps_numeric_difference) |
| PH-C23b | `test_dashboard_and_history_remaining_text_uses_tag` | READY | [history-tags](cases/history-tags.md#ph-c23b--test_dashboard_and_history_remaining_text_uses_tag) |
| PH-C24a | `test_tag_invalid_and_nonfinite_inputs_need_contract` | POLICY_BLOCKED | [history-tags](cases/history-tags.md#ph-c24a--test_tag_invalid_and_nonfinite_inputs_need_contract) |
| PH-C24b | `test_negative_or_huge_tag_operands_need_contract` | POLICY_BLOCKED | [history-tags](cases/history-tags.md#ph-c24b--test_negative_or_huge_tag_operands_need_contract) |
| PH-C25a | `test_xlsx_content_totals_and_typed_hours` | READY | [exports](cases/exports.md#ph-c25a--test_xlsx_content_totals_and_typed_hours) |
| PH-C25b | `test_xlsx_total_fill_thresholds_and_event_wrapping` | READY | [exports](cases/exports.md#ph-c25b--test_xlsx_total_fill_thresholds_and_event_wrapping) |
| PH-C26a | `test_export_actor_permissions_require_policy` | POLICY_BLOCKED | [exports](cases/exports.md#ph-c26a--test_export_actor_permissions_require_policy) |
| PH-C26b | `test_export_year_owner_and_active_scope_require_policy` | POLICY_BLOCKED | [exports](cases/exports.md#ph-c26b--test_export_year_owner_and_active_scope_require_policy) |
| PH-C27a | `test_same_name_active_owners_keep_separate_export_totals` | NEEDS_FIX | [exports](cases/exports.md#ph-c27a--test_same_name_active_owners_keep_separate_export_totals) |
| PH-C27b | `test_username_and_full_name_collision_requires_export_scope` | POLICY_BLOCKED | [exports](cases/exports.md#ph-c27b--test_username_and_full_name_collision_requires_export_scope) |
| PH-C28a | `test_equals_prefixed_user_content_is_never_formula_typed` | NEEDS_FIX | [exports](cases/exports.md#ph-c28a--test_equals_prefixed_user_content_is_never_formula_typed) |
| PH-C28b | `test_other_formula_like_prefixes_need_client_protection_policy` | POLICY_BLOCKED | [exports](cases/exports.md#ph-c28b--test_other_formula_like_prefixes_need_client_protection_policy) |
| PH-C28c | `test_unicode_and_plain_multiline_export_text_round_trips` | READY | [exports](cases/exports.md#ph-c28c--test_unicode_and_plain_multiline_export_text_round_trips) |
| PH-C29a | `test_export_with_no_approved_events_is_readable_empty_workbook` | READY | [exports](cases/exports.md#ph-c29a--test_export_with_no_approved_events_is_readable_empty_workbook) |
| PH-C29b | `test_workbook_serialization_failure_is_controlled` | NEEDS_FIX | [exports](cases/exports.md#ph-c29b--test_workbook_serialization_failure_is_controlled) |
| PH-C30a | `test_admin_list_obeys_staff_and_model_permissions` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c30a--test_admin_list_obeys_staff_and_model_permissions) |
| PH-C30b | `test_admin_permission_denied_add_and_change_do_not_write` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c30b--test_admin_permission_denied_add_and_change_do_not_write) |
| PH-C30c | `test_admin_permission_sets_do_not_imply_domain_roles` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c30c--test_admin_permission_sets_do_not_imply_domain_roles) |
| PH-C31a | `test_admin_adds_integer_event_and_django_log` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c31a--test_admin_adds_integer_event_and_django_log) |
| PH-C31b | `test_admin_change_authority_and_domain_audit_need_policy` | POLICY_BLOCKED | [admin-lifecycle](cases/admin-lifecycle.md#ph-c31b--test_admin_change_authority_and_domain_audit_need_policy) |
| PH-C31c | `test_admin_model_form_rejects_invalid_fields_without_logs` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c31c--test_admin_model_form_rejects_invalid_fields_without_logs) |
| PH-C31d | `test_admin_negative_hours_need_business_parity_policy` | POLICY_BLOCKED | [admin-lifecycle](cases/admin-lifecycle.md#ph-c31d--test_admin_negative_hours_need_business_parity_policy) |
| PH-C32a | `test_admin_delete_confirmation_does_not_delete` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32a--test_admin_delete_confirmation_does_not_delete) |
| PH-C32b | `test_admin_single_delete_needs_retention_policy` | POLICY_BLOCKED | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32b--test_admin_single_delete_needs_retention_policy) |
| PH-C32c | `test_admin_bulk_delete_needs_retention_policy` | POLICY_BLOCKED | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32c--test_admin_bulk_delete_needs_retention_policy) |
| PH-C32d | `test_admin_delete_denial_preserves_events_and_logs` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32d--test_admin_delete_denial_preserves_events_and_logs) |
| PH-C32e | `test_owner_deletion_cascade_needs_retention_policy` | POLICY_BLOCKED | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32e--test_owner_deletion_cascade_needs_retention_policy) |
| PH-C32f | `test_editor_deletion_sets_null_on_other_owners_event` | READY | [admin-lifecycle](cases/admin-lifecycle.md#ph-c32f--test_editor_deletion_sets_null_on_other_owners_event) |
| PH-C33a | `test_submit_then_approve_updates_all_approved_projections_once` | READY | [integration](cases/integration.md#ph-c33a--test_submit_then_approve_updates_all_approved_projections_once) |
| PH-C33b | `test_cross_year_edit_projection_requires_approval_policy` | POLICY_BLOCKED | [integration](cases/integration.md#ph-c33b--test_cross_year_edit_projection_requires_approval_policy) |
| PH-C33c | `test_reversed_decision_projections_need_transition_policy` | POLICY_BLOCKED | [integration](cases/integration.md#ph-c33c--test_reversed_decision_projections_need_transition_policy) |

## Original parent to replacement cases

Every original parent is retained. The replacement prose lives only in cases/;
the old dense case blocks have been removed. The final column identifies scenario
coverage shared with another parent's case without counting a duplicated design.

| Original parent | Its new case IDs | Preserved scenarios and cross-parent references |
| --- | --- | --- |
| PH-C01 | [PH-C01a](cases/access.md#ph-c01a--test_anonymous_domain_requests_require_login), [PH-C01b](cases/access.md#ph-c01b--test_non_active_actors_cannot_submit_or_read_member_pages), [PH-C01c](cases/access.md#ph-c01c--test_approval_requires_both_narrow_roles), [PH-C01d](cases/access.md#ph-c01d--test_non_chairs_cannot_read_or_post_edit), [PH-C01e](cases/access.md#ph-c01e--test_missing_profiles_are_denied_by_role_decorators), [PH-C01f](cases/access.md#ph-c01f--test_chair_without_active_edit_authority_needs_policy) | Anonymous, no-profile, exact-role denial and chair-only edit policy; export actors C26a, target visibility C22a and undeclared-role corruption C20d. |
| PH-C02 | [PH-C02a](cases/access.md#ph-c02a--test_submit_csrf_rejects_absent_or_bad_token), [PH-C02b](cases/access.md#ph-c02b--test_approve_csrf_rejects_absent_or_bad_token), [PH-C02c](cases/access.md#ph-c02c--test_deny_csrf_rejects_absent_or_bad_token), [PH-C02d](cases/access.md#ph-c02d--test_edit_csrf_rejects_absent_or_bad_token) | Missing/bad CSRF on all four mutations; real-token submit C04b, approve C09b, deny C10a and edit C14b. |
| PH-C03 | [PH-C03a](cases/access.md#ph-c03a--test_mutation_route_other_methods_need_policy), [PH-C03b](cases/access.md#ph-c03b--test_read_route_post_methods_need_policy), [PH-C03c](cases/access.md#ph-c03c--test_role_denial_uses_poll_without_referrer), [PH-C03d](cases/access.md#ph-c03d--test_role_denial_uses_safe_referrer), [PH-C03e](cases/access.md#ph-c03e--test_role_denial_rejects_external_referrer) | PUT/PATCH/DELETE, POST on read routes, safe/no/external referrers; session identity and no-write assertions. |
| PH-C04 | [PH-C04a](cases/submissions.md#ph-c04a--test_submission_form_exposes_three_fields), [PH-C04b](cases/submissions.md#ph-c04b--test_integer_submission_persists_exact_values), [PH-C04c](cases/submissions.md#ph-c04c--test_submitted_owner_status_and_audit_are_ignored) | GET form, own integer values, request time, null audit and forged owner/status/audit. |
| PH-C05 | [PH-C05a](cases/submissions.md#ph-c05a--test_submission_rejects_below_minimum_hours), [PH-C05b](cases/submissions.md#ph-c05b--test_integral_float_string_preserves_integer_hours), [PH-C05c](cases/submissions.md#ph-c05c--test_fractional_submission_requires_precision_policy), [PH-C05d](cases/submissions.md#ph-c05d--test_edit_minimum_and_fractional_hours_require_policy) | Below-minimum preservation; integral float input; fractional/step storage and edit minimum policy. |
| PH-C06 | [PH-C06a](cases/submissions.md#ph-c06a--test_submission_parse_errors_leave_no_event), [PH-C06b](cases/submissions.md#ph-c06b--test_submission_nonfinite_hours_create_no_record), [PH-C06c](cases/submissions.md#ph-c06c--test_edit_invalid_hours_returns_controlled_error), [PH-C06d](cases/submissions.md#ph-c06d--test_huge_finite_hours_need_upper_bound) | Missing/blank/malformed/non-finite hours, large finite values, edit errors and unchanged editor/time. |
| PH-C07 | [PH-C07a](cases/submissions.md#ph-c07a--test_missing_submission_keys_and_bad_dates_do_not_write), [PH-C07b](cases/submissions.md#ph-c07b--test_empty_and_overlong_titles_require_validation_policy), [PH-C07c](cases/submissions.md#ph-c07c--test_hundred_character_title_round_trips), [PH-C07d](cases/submissions.md#ph-c07d--test_unicode_and_html_title_render_as_text), [PH-C07e](cases/submissions.md#ph-c07e--test_past_and_future_event_dates_need_policy) | Missing keys/bad dates, blank/whitespace/100/101-char/Unicode/script titles and past/future policy; edit field failures C15c. |
| PH-C08 | [PH-C08a](cases/submissions.md#ph-c08a--test_submit_prewrite_save_failure_is_reported_without_row), [PH-C08b](cases/submissions.md#ph-c08b--test_identical_submit_retry_requires_idempotency_policy), [PH-C08c](cases/submissions.md#ph-c08c--test_submit_postwrite_exception_needs_commit_policy), [PH-C08d](cases/submissions.md#ph-c08d--test_submission_does_not_disclose_save_exception_details) | Pre-write failure, duplicate retry, post-write failure and raw error disclosure. |
| PH-C09 | [PH-C09a](cases/approvals.md#ph-c09a--test_pending_list_contains_only_requested_rows_by_date), [PH-C09b](cases/approvals.md#ph-c09b--test_initial_approval_updates_only_decision_fields) | Pending across owners/date order and initial approval audit/unchanged metadata. |
| PH-C10 | [PH-C10a](cases/approvals.md#ph-c10a--test_initial_denial_updates_only_decision_fields), [PH-C10b](cases/approvals.md#ph-c10b--test_denied_event_remains_personal_but_not_approved_history) | Initial denial and own/approved-history projections; denied workbook exclusion C25a. |
| PH-C11 | [PH-C11a](cases/approvals.md#ph-c11a--test_bad_decision_event_ids_report_error_without_write), [PH-C11b](cases/approvals.md#ph-c11b--test_unknown_decision_action_cannot_report_success), [PH-C11c](cases/approvals.md#ph-c11c--test_decision_helper_nonpost_is_noop), [PH-C11d](cases/approvals.md#ph-c11d--test_direct_decision_callable_needs_authorization_boundary) | Missing/nonexistent/noninteger IDs, omitted/unknown actions, direct non-POST no-op and direct-call authorization. |
| PH-C12 | [PH-C12a](cases/approvals.md#ph-c12a--test_approved_to_approve_requires_transition_policy), [PH-C12b](cases/approvals.md#ph-c12b--test_denied_to_deny_requires_transition_policy), [PH-C12c](cases/approvals.md#ph-c12c--test_approved_to_deny_requires_transition_policy), [PH-C12d](cases/approvals.md#ph-c12d--test_denied_to_approve_requires_transition_policy), [PH-C12e](cases/approvals.md#ph-c12e--test_self_approve_requires_review_policy), [PH-C12f](cases/approvals.md#ph-c12f--test_self_deny_requires_review_policy) | Repeated approve/deny, reverse both directions and self approve/deny. |
| PH-C13 | [PH-C13a](cases/approvals.md#ph-c13a--test_decision_prewrite_save_failure_preserves_request), [PH-C13b](cases/approvals.md#ph-c13b--test_decision_postwrite_exception_needs_commit_policy), [PH-C13c](cases/approvals.md#ph-c13c--test_competing_approve_and_deny_need_conflict_policy) | Pre/post-write failure and competing approve-versus-deny PostgreSQL race. |
| PH-C14 | [PH-C14a](cases/edits.md#ph-c14a--test_edit_get_populates_form_without_audit_write), [PH-C14b](cases/edits.md#ph-c14b--test_chair_edit_field_whitelist_needs_reapproval_policy), [PH-C14c](cases/edits.md#ph-c14c--test_second_edit_needs_latest_editor_and_audit_policy) | Edit form, all status/owner targets, forged metadata, editor/time and repeated latest-editor changes; chair-only rule C01f. |
| PH-C15 | [PH-C15a](cases/edits.md#ph-c15a--test_unknown_numeric_edit_target_is_404), [PH-C15b](cases/edits.md#ph-c15b--test_noninteger_edit_paths_do_not_resolve), [PH-C15c](cases/edits.md#ph-c15c--test_edit_missing_title_or_bad_date_is_controlled) | Missing/noninteger/negative paths and missing title/date edit failures; malformed hours C06c. |
| PH-C16 | [PH-C16a](cases/edits.md#ph-c16a--test_edit_prewrite_failure_preserves_entire_target), [PH-C16b](cases/edits.md#ph-c16b--test_edit_postwrite_exception_needs_commit_policy), [PH-C16c](cases/edits.md#ph-c16c--test_stale_edit_and_approval_need_conflict_policy), [PH-C16d](cases/edits.md#ph-c16d--test_competing_edits_need_conflict_policy) | Edit pre/post-write failures, stale edit versus approval and edit-versus-edit races. |
| PH-C17 | [PH-C17a](cases/statistics.md#ph-c17a--test_academic_year_dates_are_july_through_june), [PH-C17b](cases/statistics.md#ph-c17b--test_available_years_before_and_after_july), [PH-C17c](cases/statistics.md#ph-c17c--test_available_year_count_can_be_zero_or_one), [PH-C17d](cases/statistics.md#ph-c17d--test_dashboard_default_year_before_july), [PH-C17e](cases/statistics.md#ph-c17e--test_dashboard_default_year_from_july), [PH-C17f](cases/statistics.md#ph-c17f--test_explicit_dashboard_year_overrides_clock), [PH-C17g](cases/statistics.md#ph-c17g--test_date_helper_invalid_arguments_need_contract) | July/June date helpers, available-year default/count, clock boundary, explicit override and invalid helper inputs. |
| PH-C18 | [PH-C18a](cases/statistics.md#ph-c18a--test_chapter_and_personal_approved_totals_are_scoped), [PH-C18b](cases/statistics.md#ph-c18b--test_goal_threshold_is_ten_approved_hours), [PH-C18c](cases/statistics.md#ph-c18c--test_multiple_nonactive_roles_do_not_duplicate_statistics) | Approved-only chapter/personal math, zero members, threshold variants and multiple-role deduplication; remaining tag C23a. |
| PH-C19 | [PH-C19a](cases/statistics.md#ph-c19a--test_year_range_includes_july_first_and_june_thirtieth), [PH-C19b](cases/statistics.md#ph-c19b--test_empty_selected_year_retains_zero_active_members), [PH-C19c](cases/statistics.md#ph-c19c--test_statistics_empty_profile_input_returns_zeroes), [PH-C19d](cases/statistics.md#ph-c19d--test_unwrapped_dashboard_zero_denominator_is_safe) | Inclusive range, empty selected AY, empty helper input and real-ORM zero denominator branch. |
| PH-C20 | [PH-C20a](cases/statistics.md#ph-c20a--test_invalid_dashboard_year_is_a_controlled_error), [PH-C20b](cases/statistics.md#ph-c20b--test_historical_year_outside_dropdown_needs_range_policy), [PH-C20c](cases/statistics.md#ph-c20c--test_declared_chair_dashboard_flag_needs_canonical_role_policy), [PH-C20d](cases/statistics.md#ph-c20d--test_undeclared_chair_role_cannot_gain_decision_permissions) | Malformed/extreme selected years, outside-dropdown history, canonical chair flag and intentional invalid role. |
| PH-C21 | [PH-C21a](cases/history-tags.md#ph-c21a--test_history_helper_buckets_approved_events_and_lifetime), [PH-C21b](cases/history-tags.md#ph-c21b--test_own_history_view_renders_approved_only), [PH-C21c](cases/history-tags.md#ph-c21c--test_empty_approved_history_renders_zero_and_empty_text), [PH-C21d](cases/history-tags.md#ph-c21d--test_history_marks_edited_event), [PH-C21e](cases/history-tags.md#ph-c21e--test_history_edit_link_tracks_declared_chair_role) | Approved year/lifetime buckets/order, own view, empty history, edited marker and edit links. |
| PH-C22 | [PH-C22a](cases/history-tags.md#ph-c22a--test_other_and_inactive_history_visibility_needs_policy), [PH-C22b](cases/history-tags.md#ph-c22b--test_missing_target_profile_redirects_without_record_changes) | Own history C21b, other/inactive visibility and missing/profileless target; caller authentication C01a/e. |
| PH-C23 | [PH-C23a](cases/history-tags.md#ph-c23a--test_hours_remaining_clamps_numeric_difference), [PH-C23b](cases/history-tags.md#ph-c23b--test_dashboard_and_history_remaining_text_uses_tag) | Finite numeric/string arithmetic, clamp and dashboard/history remaining text; escaping C07d. |
| PH-C24 | [PH-C24a](cases/history-tags.md#ph-c24a--test_tag_invalid_and_nonfinite_inputs_need_contract), [PH-C24b](cases/history-tags.md#ph-c24b--test_negative_or_huge_tag_operands_need_contract) | None/blank/object/non-finite/negative/huge helper inputs and fallback/precondition policy. |
| PH-C25 | [PH-C25a](cases/exports.md#ph-c25a--test_xlsx_content_totals_and_typed_hours), [PH-C25b](cases/exports.md#ph-c25b--test_xlsx_total_fill_thresholds_and_event_wrapping) | XLSX MIME/filename/values/types/headers/totals, sort, no duplicates/denied rows, color boundaries and wrapping. |
| PH-C26 | [PH-C26a](cases/exports.md#ph-c26a--test_export_actor_permissions_require_policy), [PH-C26b](cases/exports.md#ph-c26b--test_export_year_owner_and_active_scope_require_policy) | Role/profile authorization, ignored year/owner scope, inactive/profileless inclusion and username fallback; anonymous C01a. |
| PH-C27 | [PH-C27a](cases/exports.md#ph-c27a--test_same_name_active_owners_keep_separate_export_totals), [PH-C27b](cases/exports.md#ph-c27b--test_username_and_full_name_collision_requires_export_scope) | Same-name ACTIVE identities and username/full-name collision without silently freezing merged totals. |
| PH-C28 | [PH-C28a](cases/exports.md#ph-c28a--test_equals_prefixed_user_content_is_never_formula_typed), [PH-C28b](cases/exports.md#ph-c28b--test_other_formula_like_prefixes_need_client_protection_policy), [PH-C28c](cases/exports.md#ph-c28c--test_unicode_and_plain_multiline_export_text_round_trips) | Equals formulas in supplied fields; other prefixes/tab/newline/client policy; Unicode/plain multiline preservation; profileless scope C26b. |
| PH-C29 | [PH-C29a](cases/exports.md#ph-c29a--test_export_with_no_approved_events_is_readable_empty_workbook), [PH-C29b](cases/exports.md#ph-c29b--test_workbook_serialization_failure_is_controlled) | Empty workbook and serializer failure/no partial attachment/no persisted file. |
| PH-C30 | [PH-C30a](cases/admin-lifecycle.md#ph-c30a--test_admin_list_obeys_staff_and_model_permissions), [PH-C30b](cases/admin-lifecycle.md#ph-c30b--test_admin_permission_denied_add_and_change_do_not_write), [PH-C30c](cases/admin-lifecycle.md#ph-c30c--test_admin_permission_sets_do_not_imply_domain_roles) | Staff/model-permission matrix, columns, add/change denied writes and exact grants; demo blanket admin boundary owned by AUTHENTICATE. |
| PH-C31 | [PH-C31a](cases/admin-lifecycle.md#ph-c31a--test_admin_adds_integer_event_and_django_log), [PH-C31b](cases/admin-lifecycle.md#ph-c31b--test_admin_change_authority_and_domain_audit_need_policy), [PH-C31c](cases/admin-lifecycle.md#ph-c31c--test_admin_model_form_rejects_invalid_fields_without_logs), [PH-C31d](cases/admin-lifecycle.md#ph-c31d--test_admin_negative_hours_need_business_parity_policy) | Admin integer add/log, change/owner/status/domain audit policy, invalid model form and negative-hour parity. |
| PH-C32 | [PH-C32a](cases/admin-lifecycle.md#ph-c32a--test_admin_delete_confirmation_does_not_delete), [PH-C32b](cases/admin-lifecycle.md#ph-c32b--test_admin_single_delete_needs_retention_policy), [PH-C32c](cases/admin-lifecycle.md#ph-c32c--test_admin_bulk_delete_needs_retention_policy), [PH-C32d](cases/admin-lifecycle.md#ph-c32d--test_admin_delete_denial_preserves_events_and_logs), [PH-C32e](cases/admin-lifecycle.md#ph-c32e--test_owner_deletion_cascade_needs_retention_policy), [PH-C32f](cases/admin-lifecycle.md#ph-c32f--test_editor_deletion_sets_null_on_other_owners_event) | Delete confirmation, single/bulk delete policy, denied deletion, owner cascade and editor SET_NULL. |
| PH-C33 | [PH-C33a](cases/integration.md#ph-c33a--test_submit_then_approve_updates_all_approved_projections_once), [PH-C33b](cases/integration.md#ph-c33b--test_cross_year_edit_projection_requires_approval_policy), [PH-C33c](cases/integration.md#ph-c33c--test_reversed_decision_projections_need_transition_policy) | Requested-to-approved projections, cross-AY edit and reversed-decision projections without double counts. |
