# Case index and refinement mapping

[Inventory](regression-spec.md) · [Fixture contract](../../../docs/testing/fixture-contract.md)

Original groups: **55**. New atomic designs: **157**.
Primary status counts: **READY 76**, **NEEDS_FIX 3**, **POLICY_BLOCKED 78**, **INFRA_BLOCKED 0**.
No case has run. These counts do not measure code coverage or approval.

## New cases

| New ID | test_name | Primary status | Case |
| --- | --- | --- | --- |
| AUTH-A01-01a | `test_login_form` | READY | [case](cases/sessions.md#auth-a01-01a) |
| AUTH-A01-01b | `test_password_login_home` | READY | [case](cases/sessions.md#auth-a01-01b) |
| AUTH-A01-01c | `test_password_login_local_next` | READY | [case](cases/sessions.md#auth-a01-01c) |
| AUTH-A01-01d | `test_password_login_without_profile` | READY | [case](cases/sessions.md#auth-a01-01d) |
| AUTH-A01-02a | `test_reject_bad_login_credentials` | READY | [case](cases/sessions.md#auth-a01-02a) |
| AUTH-A01-02b | `test_reject_inactive_login` | READY | [case](cases/sessions.md#auth-a01-02b) |
| AUTH-A01-02c | `test_authenticated_login_get` | READY | [case](cases/sessions.md#auth-a01-02c) |
| AUTH-A01-03a | `test_reject_external_login_next` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a01-03a) |
| AUTH-A01-04a | `test_login_identity_switch` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a01-04a) |
| AUTH-A01-04b | `test_failed_login_keeps_existing_identity` | READY | [case](cases/sessions.md#auth-a01-04b) |
| AUTH-A01-04c | `test_login_other_methods` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a01-04c) |
| AUTH-A02-01a | `test_logout_clears_current_session` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a02-01a) |
| AUTH-A02-01b | `test_repeat_logout` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a02-01b) |
| AUTH-A02-02a | `test_logout_rejects_bad_csrf` | READY | [case](cases/sessions.md#auth-a02-02a) |
| AUTH-A02-02b | `test_cross_site_get_logout` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a02-02b) |
| AUTH-A03-01a | `test_password_change_keeps_current_session` | READY | [case](cases/sessions.md#auth-a03-01a) |
| AUTH-A03-01b | `test_password_change_invalidates_other_session` | READY | [case](cases/sessions.md#auth-a03-01b) |
| AUTH-A03-02a | `test_wrong_current_password` | READY | [case](cases/sessions.md#auth-a03-02a) |
| AUTH-A03-02b | `test_password_confirmation_mismatch` | READY | [case](cases/sessions.md#auth-a03-02b) |
| AUTH-A03-02c | `test_password_nonpost_policy` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-02c) |
| AUTH-A03-03a | `test_password_malformed_json` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-03a) |
| AUTH-A03-03b | `test_password_missing_or_wrong_type_fields` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-03b) |
| AUTH-A03-03c | `test_password_empty_or_oversized_boundary` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-03c) |
| AUTH-A03-04a | `test_password_reuse_strength_whitespace` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-04a) |
| AUTH-A03-04b | `test_password_user_save_failure` | POLICY_BLOCKED | [case](cases/sessions.md#auth-a03-04b) |
| AUTH-A04-01a | `test_edit_own_profile` | READY | [case](cases/profile.md#auth-a04-01a) |
| AUTH-A04-01b | `test_profile_ignores_target_and_privilege_fields` | READY | [case](cases/profile.md#auth-a04-01b) |
| AUTH-A04-01c | `test_repeat_profile_update` | READY | [case](cases/profile.md#auth-a04-01c) |
| AUTH-A04-02a | `test_profile_rejects_blacklist_field` | READY | [case](cases/profile.md#auth-a04-02a) |
| AUTH-A04-02b | `test_profile_get_rejection` | READY | [case](cases/profile.md#auth-a04-02b) |
| AUTH-A04-02c | `test_profile_accepts_exact_whitelist` | READY | [case](cases/profile.md#auth-a04-02c) |
| AUTH-A04-03a | `test_profile_duplicate_username` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-03a) |
| AUTH-A04-03b | `test_profile_missing_fields` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-03b) |
| AUTH-A04-03c | `test_profile_field_validation_boundaries` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-03c) |
| AUTH-A04-04a | `test_profile_database_second_write_failure` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-04a) |
| AUTH-A04-04b | `test_profile_image_storage_failure_after_user_write` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-04b) |
| AUTH-A04-05a | `test_profile_missing_profile_response` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-05a) |
| AUTH-A04-05b | `test_profile_text_edit_image_retention` | POLICY_BLOCKED | [case](cases/profile.md#auth-a04-05b) |
| AUTH-A10-01a | `test_profile_read_own_context` | READY | [case](cases/profile.md#auth-a10-01a) |
| AUTH-A10-01b | `test_profile_sorted_majors_and_form_payloads` | READY | [case](cases/profile.md#auth-a10-01b) |
| AUTH-A10-02a | `test_profile_url_failure_cannot_delete_reference` | POLICY_BLOCKED | [case](cases/profile.md#auth-a10-02a) |
| AUTH-A10-02b | `test_profile_missing_physical_file_policy` | POLICY_BLOCKED | [case](cases/profile.md#auth-a10-02b) |
| AUTH-A10-03a | `test_profile_read_without_profile` | POLICY_BLOCKED | [case](cases/profile.md#auth-a10-03a) |
| AUTH-A10-03b | `test_profile_read_does_not_rewrite_image` | READY | [case](cases/profile.md#auth-a10-03b) |
| AUTH-A05-01a | `test_photo_ajax_thumbnail_png` | READY | [case](cases/images.md#auth-a05-01a) |
| AUTH-A05-01b | `test_photo_form_preserves_small_jpeg` | READY | [case](cases/images.md#auth-a05-01b) |
| AUTH-A05-02a | `test_photo_successful_replacement` | READY | [case](cases/images.md#auth-a05-02a) |
| AUTH-A05-02b | `test_photo_repeat_filename_retention` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-02b) |
| AUTH-A05-02c | `test_model_save_image_reencoding_policy` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-02c) |
| AUTH-A05-03a | `test_photo_corrupt_upload_retains_old_image` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-03a) |
| AUTH-A05-03b | `test_photo_format_contenttype_policy` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-03b) |
| AUTH-A05-03c | `test_photo_size_dimension_boundaries` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-03c) |
| AUTH-A05-04a | `test_photo_old_delete_failure` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-04a) |
| AUTH-A05-04b | `test_photo_new_storage_save_failure` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-04b) |
| AUTH-A05-04c | `test_photo_database_failure_after_new_file` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-04c) |
| AUTH-A05-04d | `test_photo_response_lookup_failure_after_save` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-04d) |
| AUTH-A05-05a | `test_photo_missing_upload_is_noop` | READY | [case](cases/images.md#auth-a05-05a) |
| AUTH-A05-05b | `test_photo_without_profile` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-05b) |
| AUTH-A05-05c | `test_photo_storage_without_local_path` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-05c) |
| AUTH-A05-05d | `test_model_animation_alpha_format_policy` | POLICY_BLOCKED | [case](cases/images.md#auth-a05-05d) |
| AUTH-A06-01a | `test_reset_photo_removes_own_file` | READY | [case](cases/images.md#auth-a06-01a) |
| AUTH-A06-01b | `test_reset_photo_without_image_idempotent` | READY | [case](cases/images.md#auth-a06-01b) |
| AUTH-A06-02a | `test_reset_photo_get_is_noop` | READY | [case](cases/images.md#auth-a06-02a) |
| AUTH-A06-02b | `test_reset_without_profile` | POLICY_BLOCKED | [case](cases/images.md#auth-a06-02b) |
| AUTH-A06-03a | `test_reset_storage_delete_failure` | POLICY_BLOCKED | [case](cases/images.md#auth-a06-03a) |
| AUTH-A06-03b | `test_reset_implicit_database_save_failure` | POLICY_BLOCKED | [case](cases/images.md#auth-a06-03b) |
| AUTH-A06-03c | `test_reset_final_database_save_failure` | POLICY_BLOCKED | [case](cases/images.md#auth-a06-03c) |
| AUTH-A07-01a | `test_replace_own_major_set` | READY | [case](cases/majors.md#auth-a07-01a) |
| AUTH-A07-01b | `test_clear_own_major_set` | READY | [case](cases/majors.md#auth-a07-01b) |
| AUTH-A07-02a | `test_major_selection_missing_key` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-02a) |
| AUTH-A07-02b | `test_major_selection_json_shape` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-02b) |
| AUTH-A07-02c | `test_major_selection_name_validation` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-02c) |
| AUTH-A07-02d | `test_major_selection_count_boundary` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-02d) |
| AUTH-A07-03a | `test_major_creation_mid_replace_failure` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-03a) |
| AUTH-A07-03b | `test_major_add_mid_replace_failure` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-03b) |
| AUTH-A07-04a | `test_major_selection_get_noop` | READY | [case](cases/majors.md#auth-a07-04a) |
| AUTH-A07-04b | `test_major_selection_no_profile` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-04b) |
| AUTH-A07-04c | `test_major_selection_preexisting_duplicates` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-04c) |
| AUTH-A07-04d | `test_repeat_major_replacement` | READY | [case](cases/majors.md#auth-a07-04d) |
| AUTH-A07-04e | `test_concurrent_major_replacement_policy` | POLICY_BLOCKED | [case](cases/majors.md#auth-a07-04e) |
| AUTH-A08-01a | `test_custom_major_normalization` | READY | [case](cases/majors.md#auth-a08-01a) |
| AUTH-A08-01b | `test_custom_major_sequential_idempotency` | READY | [case](cases/majors.md#auth-a08-01b) |
| AUTH-A08-01c | `test_custom_major_acronym_unicode_policy` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-01c) |
| AUTH-A08-02a | `test_custom_major_blacklist_rejection` | READY | [case](cases/majors.md#auth-a08-02a) |
| AUTH-A08-02b | `test_custom_major_get_noop` | READY | [case](cases/majors.md#auth-a08-02b) |
| AUTH-A08-03a | `test_custom_major_empty_or_typed_payload` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-03a) |
| AUTH-A08-03b | `test_custom_major_no_profile_catalog_policy` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-03b) |
| AUTH-A08-03c | `test_custom_major_browser_markup_safety` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-03c) |
| AUTH-A08-04a | `test_custom_major_existing_duplicate_resolution` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-04a) |
| AUTH-A08-04b | `test_custom_major_postgresql_race` | POLICY_BLOCKED | [case](cases/majors.md#auth-a08-04b) |
| AUTH-A09-01a | `test_dashboard_non_newmember_render` | READY | [case](cases/visibility.md#auth-a09-01a) |
| AUTH-A09-01b | `test_dashboard_newmember_precedence` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-01b) |
| AUTH-A09-01c | `test_dashboard_missing_profile` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-01c) |
| AUTH-A09-02a | `test_dashboard_links_and_active_announcements` | READY | [case](cases/visibility.md#auth-a09-02a) |
| AUTH-A09-02b | `test_dashboard_empty_content` | READY | [case](cases/visibility.md#auth-a09-02b) |
| AUTH-A09-03a | `test_roster_partition_order_and_class_policy` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-03a) |
| AUTH-A09-03b | `test_roster_ties_and_missing_names` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-03b) |
| AUTH-A09-04a | `test_roster_sensitive_field_visibility` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-04a) |
| AUTH-A09-04b | `test_roster_literal_text_escaping` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-04b) |
| AUTH-A09-04c | `test_media_access_policy` | POLICY_BLOCKED | [case](cases/visibility.md#auth-a09-04c) |
| AUTH-A11-01a | `test_filter_clean_and_whitelist_inputs` | READY | [case](cases/helpers.md#auth-a11-01a) |
| AUTH-A11-01b | `test_filter_independent_blacklist_substring` | READY | [case](cases/helpers.md#auth-a11-01b) |
| AUTH-A11-02a | `test_filter_whitelist_cannot_hide_bad_term` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-02a) |
| AUTH-A11-02b | `test_filter_benign_substring_and_types` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-02b) |
| AUTH-A11-02c | `test_unused_cleaner_definition` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-02c) |
| AUTH-A11-03a | `test_cleanup_catalog_and_global_links` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-03a) |
| AUTH-A11-03b | `test_cleanup_repeat_noop` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-03b) |
| AUTH-A11-04a | `test_cleanup_command_count_output` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-04a) |
| AUTH-A11-04b | `test_cleanup_second_delete_failure` | POLICY_BLOCKED | [case](cases/helpers.md#auth-a11-04b) |
| AUTH-C03-01a | `test_identity_role_and_profile_constraints` | READY | [case](cases/identity-admin.md#auth-c03-01a) |
| AUTH-C03-01b | `test_user_delete_profile_cascade` | READY | [case](cases/identity-admin.md#auth-c03-01b) |
| AUTH-C03-01c | `test_orphan_profile_database_semantics` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-01c) |
| AUTH-C03-01d | `test_creation_form_hashes_without_privileges` | READY | [case](cases/identity-admin.md#auth-c03-01d) |
| AUTH-C03-01e | `test_creation_form_validation` | READY | [case](cases/identity-admin.md#auth-c03-01e) |
| AUTH-C03-02a | `test_all_role_gate_requires_each_role` | READY | [case](cases/identity-admin.md#auth-c03-02a) |
| AUTH-C03-02b | `test_all_role_gate_accepts_complete_set` | READY | [case](cases/identity-admin.md#auth-c03-02b) |
| AUTH-C03-02c | `test_role_gate_anonymous_and_missing_profile` | READY | [case](cases/identity-admin.md#auth-c03-02c) |
| AUTH-C03-02d | `test_role_gate_local_referrer` | READY | [case](cases/identity-admin.md#auth-c03-02d) |
| AUTH-C03-02e | `test_role_gate_external_referrer` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-02e) |
| AUTH-C03-02f | `test_role_gate_empty_requirement_policy` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-02f) |
| AUTH-C03-03a | `test_admin_rejects_nonstaff_domain_executive` | READY | [case](cases/identity-admin.md#auth-c03-03a) |
| AUTH-C03-03b | `test_admin_staff_without_model_permissions` | READY | [case](cases/identity-admin.md#auth-c03-03b) |
| AUTH-C03-03c | `test_admin_forged_user_privilege_fields` | READY | [case](cases/identity-admin.md#auth-c03-03c) |
| AUTH-C03-03d | `test_admin_user_missing_profile_display` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-03d) |
| AUTH-C03-04a | `test_admin_authorized_profile_image_roles` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-04a) |
| AUTH-C03-04b | `test_admin_image_failure_consistency` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-04b) |
| AUTH-C03-04c | `test_unused_profile_form_commit_false` | NEEDS_FIX | [case](cases/identity-admin.md#auth-c03-04c) |
| AUTH-C03-04d | `test_unused_profile_form_unsaved_instance` | NEEDS_FIX | [case](cases/identity-admin.md#auth-c03-04d) |
| AUTH-C03-05a | `test_admin_major_and_link_edit` | READY | [case](cases/identity-admin.md#auth-c03-05a) |
| AUTH-C03-05b | `test_admin_role_invalid_choice` | READY | [case](cases/identity-admin.md#auth-c03-05b) |
| AUTH-C03-05c | `test_model_admin_display_labels` | READY | [case](cases/identity-admin.md#auth-c03-05c) |
| AUTH-C03-05d | `test_invalid_legacy_role_repair_policy` | POLICY_BLOCKED | [case](cases/identity-admin.md#auth-c03-05d) |
| AUTH-D01-01a | `test_demo_persona_entry_identity` | READY | [case](cases/demo.md#auth-d01-01a) |
| AUTH-D01-01b | `test_demo_default_persona` | READY | [case](cases/demo.md#auth-d01-01b) |
| AUTH-D01-01c | `test_demo_entry_after_username_change` | READY | [case](cases/demo.md#auth-d01-01c) |
| AUTH-D01-01d | `test_demo_newmember_dashboard_redirect` | READY | [case](cases/demo.md#auth-d01-01d) |
| AUTH-D01-02a | `test_demo_entry_post_only` | READY | [case](cases/demo.md#auth-d01-02a) |
| AUTH-D01-02b | `test_demo_unknown_persona` | READY | [case](cases/demo.md#auth-d01-02b) |
| AUTH-D01-02c | `test_demo_entry_disabled` | READY | [case](cases/demo.md#auth-d01-02c) |
| AUTH-D01-02d | `test_demo_json_content_type_policy` | POLICY_BLOCKED | [case](cases/demo.md#auth-d01-02d) |
| AUTH-D01-03a | `test_demo_ineligible_account_rejected` | READY | [case](cases/demo.md#auth-d01-03a) |
| AUTH-D01-03b | `test_demo_group_membership_trust_policy` | POLICY_BLOCKED | [case](cases/demo.md#auth-d01-03b) |
| AUTH-D01-04a | `test_demo_csrf_rejects_absent_and_bad_tokens` | READY | [case](cases/demo.md#auth-d01-04a) |
| AUTH-D01-04b | `test_demo_csrf_accepts_token_and_rotates_identity` | READY | [case](cases/demo.md#auth-d01-04b) |
| AUTH-D03-01a | `test_demo_admin_http_boundary` | READY | [case](cases/demo.md#auth-d03-01a) |
| AUTH-D03-01b | `test_demo_admin_middleware_short_circuit` | READY | [case](cases/demo.md#auth-d03-01b) |
| AUTH-D03-02a | `test_demo_custom_admin_prefix` | NEEDS_FIX | [case](cases/demo.md#auth-d03-02a) |
| AUTH-D03-02b | `test_demo_prefix_edge_paths` | POLICY_BLOCKED | [case](cases/demo.md#auth-d03-02b) |
| AUTH-S01a | `test_anonymous_protected_routes` | READY | [case](cases/http-boundaries.md#auth-s01a) |
| AUTH-S01b | `test_anonymous_protected_post_routes` | READY | [case](cases/http-boundaries.md#auth-s01b) |
| AUTH-S01c | `test_own_mutations_ignore_foreign_target_fields` | READY | [case](cases/http-boundaries.md#auth-s01c) |
| AUTH-S02a | `test_csrf_rejects_profile_mutation_tokens` | READY | [case](cases/http-boundaries.md#auth-s02a) |
| AUTH-S02b | `test_csrf_accepts_real_profile_tokens` | READY | [case](cases/http-boundaries.md#auth-s02b) |
| AUTH-S02c | `test_login_csrf_token_boundary` | READY | [case](cases/http-boundaries.md#auth-s02c) |
| AUTH-S02d | `test_other_mutation_methods_policy` | POLICY_BLOCKED | [case](cases/http-boundaries.md#auth-s02d) |
| AUTH-A03-01c | `test_password_change_without_profile` | READY | [case](cases/sessions.md#auth-a03-01c) |
| AUTH-C03-03e | `test_admin_superuser_without_domain_roles` | READY | [case](cases/identity-admin.md#auth-c03-03e) |

## Original to new mapping

Every old group remains a parent; suffixes distinguish independent contracts.
Cross-cutting CSRF is owned by S02, while D01 owns demo CSRF and A02 owns logout
CSRF. Workflow cases test accepted state changes rather than duplicating those
denial matrices. S01 owns anonymous requests and shared target-ID checks;
A04 separately owns forged profile privilege fields. No old dense case prose remains.

| Original parent | New IDs |
| --- | --- |
| AUTH-A01-01 | [AUTH-A01-01a](cases/sessions.md#auth-a01-01a), [AUTH-A01-01b](cases/sessions.md#auth-a01-01b), [AUTH-A01-01c](cases/sessions.md#auth-a01-01c), [AUTH-A01-01d](cases/sessions.md#auth-a01-01d) |
| AUTH-A01-02 | [AUTH-A01-02a](cases/sessions.md#auth-a01-02a), [AUTH-A01-02b](cases/sessions.md#auth-a01-02b), [AUTH-A01-02c](cases/sessions.md#auth-a01-02c) |
| AUTH-A01-03 | [AUTH-A01-03a](cases/sessions.md#auth-a01-03a) |
| AUTH-A01-04 | [AUTH-A01-04a](cases/sessions.md#auth-a01-04a), [AUTH-A01-04b](cases/sessions.md#auth-a01-04b), [AUTH-A01-04c](cases/sessions.md#auth-a01-04c) |
| AUTH-A02-01 | [AUTH-A02-01a](cases/sessions.md#auth-a02-01a), [AUTH-A02-01b](cases/sessions.md#auth-a02-01b) |
| AUTH-A02-02 | [AUTH-A02-02a](cases/sessions.md#auth-a02-02a), [AUTH-A02-02b](cases/sessions.md#auth-a02-02b) |
| AUTH-A03-01 | [AUTH-A03-01a](cases/sessions.md#auth-a03-01a), [AUTH-A03-01b](cases/sessions.md#auth-a03-01b), [AUTH-A03-01c](cases/sessions.md#auth-a03-01c) |
| AUTH-A03-02 | [AUTH-A03-02a](cases/sessions.md#auth-a03-02a), [AUTH-A03-02b](cases/sessions.md#auth-a03-02b), [AUTH-A03-02c](cases/sessions.md#auth-a03-02c) |
| AUTH-A03-03 | [AUTH-A03-03a](cases/sessions.md#auth-a03-03a), [AUTH-A03-03b](cases/sessions.md#auth-a03-03b), [AUTH-A03-03c](cases/sessions.md#auth-a03-03c) |
| AUTH-A03-04 | [AUTH-A03-04a](cases/sessions.md#auth-a03-04a), [AUTH-A03-04b](cases/sessions.md#auth-a03-04b) |
| AUTH-A04-01 | [AUTH-A04-01a](cases/profile.md#auth-a04-01a), [AUTH-A04-01b](cases/profile.md#auth-a04-01b), [AUTH-A04-01c](cases/profile.md#auth-a04-01c) |
| AUTH-A04-02 | [AUTH-A04-02a](cases/profile.md#auth-a04-02a), [AUTH-A04-02b](cases/profile.md#auth-a04-02b), [AUTH-A04-02c](cases/profile.md#auth-a04-02c) |
| AUTH-A04-03 | [AUTH-A04-03a](cases/profile.md#auth-a04-03a), [AUTH-A04-03b](cases/profile.md#auth-a04-03b), [AUTH-A04-03c](cases/profile.md#auth-a04-03c) |
| AUTH-A04-04 | [AUTH-A04-04a](cases/profile.md#auth-a04-04a), [AUTH-A04-04b](cases/profile.md#auth-a04-04b) |
| AUTH-A04-05 | [AUTH-A04-05a](cases/profile.md#auth-a04-05a), [AUTH-A04-05b](cases/profile.md#auth-a04-05b) |
| AUTH-A05-01 | [AUTH-A05-01a](cases/images.md#auth-a05-01a), [AUTH-A05-01b](cases/images.md#auth-a05-01b) |
| AUTH-A05-02 | [AUTH-A05-02a](cases/images.md#auth-a05-02a), [AUTH-A05-02b](cases/images.md#auth-a05-02b), [AUTH-A05-02c](cases/images.md#auth-a05-02c) |
| AUTH-A05-03 | [AUTH-A05-03a](cases/images.md#auth-a05-03a), [AUTH-A05-03b](cases/images.md#auth-a05-03b), [AUTH-A05-03c](cases/images.md#auth-a05-03c) |
| AUTH-A05-04 | [AUTH-A05-04a](cases/images.md#auth-a05-04a), [AUTH-A05-04b](cases/images.md#auth-a05-04b), [AUTH-A05-04c](cases/images.md#auth-a05-04c), [AUTH-A05-04d](cases/images.md#auth-a05-04d) |
| AUTH-A05-05 | [AUTH-A05-05a](cases/images.md#auth-a05-05a), [AUTH-A05-05b](cases/images.md#auth-a05-05b), [AUTH-A05-05c](cases/images.md#auth-a05-05c), [AUTH-A05-05d](cases/images.md#auth-a05-05d) |
| AUTH-A06-01 | [AUTH-A06-01a](cases/images.md#auth-a06-01a), [AUTH-A06-01b](cases/images.md#auth-a06-01b) |
| AUTH-A06-02 | [AUTH-A06-02a](cases/images.md#auth-a06-02a), [AUTH-A06-02b](cases/images.md#auth-a06-02b) |
| AUTH-A06-03 | [AUTH-A06-03a](cases/images.md#auth-a06-03a), [AUTH-A06-03b](cases/images.md#auth-a06-03b), [AUTH-A06-03c](cases/images.md#auth-a06-03c) |
| AUTH-A07-01 | [AUTH-A07-01a](cases/majors.md#auth-a07-01a), [AUTH-A07-01b](cases/majors.md#auth-a07-01b) |
| AUTH-A07-02 | [AUTH-A07-02a](cases/majors.md#auth-a07-02a), [AUTH-A07-02b](cases/majors.md#auth-a07-02b), [AUTH-A07-02c](cases/majors.md#auth-a07-02c), [AUTH-A07-02d](cases/majors.md#auth-a07-02d) |
| AUTH-A07-03 | [AUTH-A07-03a](cases/majors.md#auth-a07-03a), [AUTH-A07-03b](cases/majors.md#auth-a07-03b) |
| AUTH-A07-04 | [AUTH-A07-04a](cases/majors.md#auth-a07-04a), [AUTH-A07-04b](cases/majors.md#auth-a07-04b), [AUTH-A07-04c](cases/majors.md#auth-a07-04c), [AUTH-A07-04d](cases/majors.md#auth-a07-04d), [AUTH-A07-04e](cases/majors.md#auth-a07-04e) |
| AUTH-A08-01 | [AUTH-A08-01a](cases/majors.md#auth-a08-01a), [AUTH-A08-01b](cases/majors.md#auth-a08-01b), [AUTH-A08-01c](cases/majors.md#auth-a08-01c) |
| AUTH-A08-02 | [AUTH-A08-02a](cases/majors.md#auth-a08-02a), [AUTH-A08-02b](cases/majors.md#auth-a08-02b) |
| AUTH-A08-03 | [AUTH-A08-03a](cases/majors.md#auth-a08-03a), [AUTH-A08-03b](cases/majors.md#auth-a08-03b), [AUTH-A08-03c](cases/majors.md#auth-a08-03c) |
| AUTH-A08-04 | [AUTH-A08-04a](cases/majors.md#auth-a08-04a), [AUTH-A08-04b](cases/majors.md#auth-a08-04b) |
| AUTH-A11-01 | [AUTH-A11-01a](cases/helpers.md#auth-a11-01a), [AUTH-A11-01b](cases/helpers.md#auth-a11-01b) |
| AUTH-A11-02 | [AUTH-A11-02a](cases/helpers.md#auth-a11-02a), [AUTH-A11-02b](cases/helpers.md#auth-a11-02b), [AUTH-A11-02c](cases/helpers.md#auth-a11-02c) |
| AUTH-A11-03 | [AUTH-A11-03a](cases/helpers.md#auth-a11-03a), [AUTH-A11-03b](cases/helpers.md#auth-a11-03b) |
| AUTH-A11-04 | [AUTH-A11-04a](cases/helpers.md#auth-a11-04a), [AUTH-A11-04b](cases/helpers.md#auth-a11-04b) |
| AUTH-A09-01 | [AUTH-A09-01a](cases/visibility.md#auth-a09-01a), [AUTH-A09-01b](cases/visibility.md#auth-a09-01b), [AUTH-A09-01c](cases/visibility.md#auth-a09-01c) |
| AUTH-A09-02 | [AUTH-A09-02a](cases/visibility.md#auth-a09-02a), [AUTH-A09-02b](cases/visibility.md#auth-a09-02b) |
| AUTH-A09-03 | [AUTH-A09-03a](cases/visibility.md#auth-a09-03a), [AUTH-A09-03b](cases/visibility.md#auth-a09-03b) |
| AUTH-A09-04 | [AUTH-A09-04a](cases/visibility.md#auth-a09-04a), [AUTH-A09-04b](cases/visibility.md#auth-a09-04b), [AUTH-A09-04c](cases/visibility.md#auth-a09-04c) |
| AUTH-A10-01 | [AUTH-A10-01a](cases/profile.md#auth-a10-01a), [AUTH-A10-01b](cases/profile.md#auth-a10-01b) |
| AUTH-A10-02 | [AUTH-A10-02a](cases/profile.md#auth-a10-02a), [AUTH-A10-02b](cases/profile.md#auth-a10-02b) |
| AUTH-A10-03 | [AUTH-A10-03a](cases/profile.md#auth-a10-03a), [AUTH-A10-03b](cases/profile.md#auth-a10-03b) |
| AUTH-C03-01 | [AUTH-C03-01a](cases/identity-admin.md#auth-c03-01a), [AUTH-C03-01b](cases/identity-admin.md#auth-c03-01b), [AUTH-C03-01c](cases/identity-admin.md#auth-c03-01c), [AUTH-C03-01d](cases/identity-admin.md#auth-c03-01d), [AUTH-C03-01e](cases/identity-admin.md#auth-c03-01e) |
| AUTH-C03-02 | [AUTH-C03-02a](cases/identity-admin.md#auth-c03-02a), [AUTH-C03-02b](cases/identity-admin.md#auth-c03-02b), [AUTH-C03-02c](cases/identity-admin.md#auth-c03-02c), [AUTH-C03-02d](cases/identity-admin.md#auth-c03-02d), [AUTH-C03-02e](cases/identity-admin.md#auth-c03-02e), [AUTH-C03-02f](cases/identity-admin.md#auth-c03-02f) |
| AUTH-C03-03 | [AUTH-C03-03a](cases/identity-admin.md#auth-c03-03a), [AUTH-C03-03b](cases/identity-admin.md#auth-c03-03b), [AUTH-C03-03c](cases/identity-admin.md#auth-c03-03c), [AUTH-C03-03d](cases/identity-admin.md#auth-c03-03d), [AUTH-C03-03e](cases/identity-admin.md#auth-c03-03e) |
| AUTH-C03-04 | [AUTH-C03-04a](cases/identity-admin.md#auth-c03-04a), [AUTH-C03-04b](cases/identity-admin.md#auth-c03-04b), [AUTH-C03-04c](cases/identity-admin.md#auth-c03-04c), [AUTH-C03-04d](cases/identity-admin.md#auth-c03-04d) |
| AUTH-C03-05 | [AUTH-C03-05a](cases/identity-admin.md#auth-c03-05a), [AUTH-C03-05b](cases/identity-admin.md#auth-c03-05b), [AUTH-C03-05c](cases/identity-admin.md#auth-c03-05c), [AUTH-C03-05d](cases/identity-admin.md#auth-c03-05d) |
| AUTH-D01-01 | [AUTH-D01-01a](cases/demo.md#auth-d01-01a), [AUTH-D01-01b](cases/demo.md#auth-d01-01b), [AUTH-D01-01c](cases/demo.md#auth-d01-01c), [AUTH-D01-01d](cases/demo.md#auth-d01-01d) |
| AUTH-D01-02 | [AUTH-D01-02a](cases/demo.md#auth-d01-02a), [AUTH-D01-02b](cases/demo.md#auth-d01-02b), [AUTH-D01-02c](cases/demo.md#auth-d01-02c), [AUTH-D01-02d](cases/demo.md#auth-d01-02d) |
| AUTH-D01-03 | [AUTH-D01-03a](cases/demo.md#auth-d01-03a), [AUTH-D01-03b](cases/demo.md#auth-d01-03b) |
| AUTH-D01-04 | [AUTH-D01-04a](cases/demo.md#auth-d01-04a), [AUTH-D01-04b](cases/demo.md#auth-d01-04b) |
| AUTH-D03-01 | [AUTH-D03-01a](cases/demo.md#auth-d03-01a), [AUTH-D03-01b](cases/demo.md#auth-d03-01b) |
| AUTH-D03-02 | [AUTH-D03-02a](cases/demo.md#auth-d03-02a), [AUTH-D03-02b](cases/demo.md#auth-d03-02b) |
| AUTH-S01 | [AUTH-S01a](cases/http-boundaries.md#auth-s01a), [AUTH-S01b](cases/http-boundaries.md#auth-s01b), [AUTH-S01c](cases/http-boundaries.md#auth-s01c) |
| AUTH-S02 | [AUTH-S02a](cases/http-boundaries.md#auth-s02a), [AUTH-S02b](cases/http-boundaries.md#auth-s02b), [AUTH-S02c](cases/http-boundaries.md#auth-s02c), [AUTH-S02d](cases/http-boundaries.md#auth-s02d) |

## Validation and handoff

Checked unique new IDs/test names, 55-parent completeness, one primary status per
case, metadata, GIVEN/WHEN/THEN blocks, index totals and relative local links.
Scenario retention was reviewed against each original parent. No application
tests, PostgreSQL races, browser cases or storage experiments ran. Source facts
remain baseline `7e25ac2`; refinement baseline is `c8bbc4e`. Coordinator must
verify source/classification and final cross-domain consistency before implementation.
