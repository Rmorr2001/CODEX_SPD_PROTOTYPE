# HOME case and readiness index

All designs are unexecuted. READY is a design status, not approval or a passing test.
See [inventory, decisions and fixture rules](regression-spec.md).

Original groups: 21. Atomic cases: 97.

| Status | Count |
| --- | --- |
| READY | 63 |
| NEEDS_FIX | 6 |
| POLICY_BLOCKED | 26 |
| INFRA_BLOCKED | 2 |

## Cases

| New ID | test_name | Primary status | Case |
| --- | --- | --- | --- |
| HOME-T01a | `test_public_routes_render_for_narrow_actors` | READY | [design](cases/public-routes.md#home-t01a--test_public_routes_render_for_narrow_actors) |
| HOME-T01b | `test_home_without_banner_omits_banner_image` | READY | [design](cases/public-routes.md#home-t01b--test_home_without_banner_omits_banner_image) |
| HOME-T01c | `test_history_empty_profile_count_is_zero` | READY | [design](cases/public-routes.md#home-t01c--test_history_empty_profile_count_is_zero) |
| HOME-T01d | `test_rush_without_slides_renders_empty_slideshow` | READY | [design](cases/public-routes.md#home-t01d--test_rush_without_slides_renders_empty_slideshow) |
| HOME-T01e | `test_board_without_officers_has_empty_message` | READY | [design](cases/public-routes.md#home-t01e--test_board_without_officers_has_empty_message) |
| HOME-T01f | `test_public_shell_without_actor_profile_uses_fallback` | READY | [design](cases/public-routes.md#home-t01f--test_public_shell_without_actor_profile_uses_fallback) |
| HOME-T02a | `test_active_count_uses_distinct_role_membership` | READY | [design](cases/public-routes.md#home-t02a--test_active_count_uses_distinct_role_membership) |
| HOME-T02b | `test_mixed_and_null_user_count_policy` | POLICY_BLOCKED | [design](cases/public-routes.md#home-t02b--test_mixed_and_null_user_count_policy) |
| HOME-T02c | `test_board_role_order_and_multi_office_pairs` | READY | [design](cases/public-routes.md#home-t02c--test_board_role_order_and_multi_office_pairs) |
| HOME-T02d | `test_board_eligibility_and_holder_tie_policy` | POLICY_BLOCKED | [design](cases/public-routes.md#home-t02d--test_board_eligibility_and_holder_tie_policy) |
| HOME-T03a | `test_slide_order_preserves_all_ties` | READY | [design](cases/public-content.md#home-t03a--test_slide_order_preserves_all_ties) |
| HOME-T03b | `test_slide_caption_and_image_attributes_escape_markup` | READY | [design](cases/public-content.md#home-t03b--test_slide_caption_and_image_attributes_escape_markup) |
| HOME-T03c | `test_board_fields_escape_injected_markup` | READY | [design](cases/public-content.md#home-t03c--test_board_fields_escape_injected_markup) |
| HOME-T03d | `test_shell_errors_messages_and_username_escape` | READY | [design](cases/public-content.md#home-t03d--test_shell_errors_messages_and_username_escape) |
| HOME-T03e | `test_configured_interest_link_renders_in_three_buttons` | READY | [design](cases/public-content.md#home-t03e--test_configured_interest_link_renders_in_three_buttons) |
| HOME-T03f | `test_board_optional_fields_use_fallbacks` | READY | [design](cases/public-content.md#home-t03f--test_board_optional_fields_use_fallbacks) |
| HOME-T04a | `test_missing_interest_link_fallback_policy` | POLICY_BLOCKED | [design](cases/public-content.md#home-t04a--test_missing_interest_link_fallback_policy) |
| HOME-T04b | `test_empty_image_reference_does_not_crash_page` | NEEDS_FIX | [design](cases/public-content.md#home-t04b--test_empty_image_reference_does_not_crash_page) |
| HOME-T04c | `test_missing_nonempty_image_keeps_page_renderable` | READY | [design](cases/public-content.md#home-t04c--test_missing_nonempty_image_keeps_page_renderable) |
| HOME-T04d | `test_unsafe_interest_url_scheme_policy` | POLICY_BLOCKED | [design](cases/public-content.md#home-t04d--test_unsafe_interest_url_scheme_policy) |
| HOME-T05a | `test_public_head_and_irrelevant_query_are_read_only` | READY | [design](cases/public-content.md#home-t05a--test_public_head_and_irrelevant_query_are_read_only) |
| HOME-T05b | `test_public_unsafe_method_policy` | POLICY_BLOCKED | [design](cases/public-content.md#home-t05b--test_public_unsafe_method_policy) |
| HOME-T05c | `test_public_unsafe_request_rejects_bad_csrf` | READY | [design](cases/public-content.md#home-t05c--test_public_unsafe_request_rejects_bad_csrf) |
| HOME-T05d | `test_slideshow_and_panel_controls_are_local` | INFRA_BLOCKED | [design](cases/public-content.md#home-t05d--test_slideshow_and_panel_controls_are_local) |
| HOME-T06a | `test_media_serves_synthetic_image_bytes` | READY | [design](cases/media-composition.md#home-t06a--test_media_serves_synthetic_image_bytes) |
| HOME-T06b | `test_missing_media_and_directories_do_not_disclose` | READY | [design](cases/media-composition.md#home-t06b--test_missing_media_and_directories_do_not_disclose) |
| HOME-T06c | `test_lexical_media_traversal_is_denied` | READY | [design](cases/media-composition.md#home-t06c--test_lexical_media_traversal_is_denied) |
| HOME-T06d | `test_media_symlink_cannot_escape_root` | NEEDS_FIX | [design](cases/media-composition.md#home-t06d--test_media_symlink_cannot_escape_root) |
| HOME-T06e | `test_public_board_and_media_visibility_policy` | POLICY_BLOCKED | [design](cases/media-composition.md#home-t06e--test_public_board_and_media_visibility_policy) |
| HOME-T07a | `test_public_templates_reference_local_assets` | READY | [design](cases/media-composition.md#home-t07a--test_public_templates_reference_local_assets) |
| HOME-T07b | `test_collected_static_assets_are_served` | INFRA_BLOCKED | [design](cases/media-composition.md#home-t07b--test_collected_static_assets_are_served) |
| HOME-T07c | `test_demo_shell_context_controls_banner` | READY | [design](cases/media-composition.md#home-t07c--test_demo_shell_context_controls_banner) |
| HOME-T07d | `test_explorer_cache_header_is_scoped` | READY | [design](cases/media-composition.md#home-t07d--test_explorer_cache_header_is_scoped) |
| HOME-T08a | `test_singleton_initial_create_persists_value` | READY | [design](cases/content-models.md#home-t08a--test_singleton_initial_create_persists_value) |
| HOME-T08b | `test_successful_singleton_replacement_has_one_new_value` | READY | [design](cases/content-models.md#home-t08b--test_successful_singleton_replacement_has_one_new_value) |
| HOME-T08c | `test_singleton_normal_update_and_repeat_remain_single` | READY | [design](cases/content-models.md#home-t08c--test_singleton_normal_update_and_repeat_remain_single) |
| HOME-T09a | `test_model_full_clean_rejects_required_and_length_errors` | READY | [design](cases/content-models.md#home-t09a--test_model_full_clean_rejects_required_and_length_errors) |
| HOME-T09b | `test_singleton_update_fields_does_not_erase_previous_row` | POLICY_BLOCKED | [design](cases/content-models.md#home-t09b--test_singleton_update_fields_does_not_erase_previous_row) |
| HOME-T09c | `test_singleton_forced_save_options_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t09c--test_singleton_forced_save_options_policy) |
| HOME-T09d | `test_bulk_and_alias_singleton_boundary_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t09d--test_bulk_and_alias_singleton_boundary_policy) |
| HOME-T09e | `test_direct_save_validation_boundary_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t09e--test_direct_save_validation_boundary_policy) |
| HOME-T10a | `test_storage_save_failure_preserves_prior_banner_row` | NEEDS_FIX | [design](cases/content-models.md#home-t10a--test_storage_save_failure_preserves_prior_banner_row) |
| HOME-T10b | `test_db_insert_failure_preserves_prior_singleton` | NEEDS_FIX | [design](cases/content-models.md#home-t10b--test_db_insert_failure_preserves_prior_singleton) |
| HOME-T10c | `test_failed_replacement_retry_preserves_then_replaces` | NEEDS_FIX | [design](cases/content-models.md#home-t10c--test_failed_replacement_retry_preserves_then_replaces) |
| HOME-T10d | `test_successful_replacement_and_delete_file_retention_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t10d--test_successful_replacement_and_delete_file_retention_policy) |
| HOME-T10e | `test_cleanup_and_orphan_failure_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t10e--test_cleanup_and_orphan_failure_policy) |
| HOME-T11a | `test_concurrent_singleton_replacement_conflict_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t11a--test_concurrent_singleton_replacement_conflict_policy) |
| HOME-T11b | `test_concurrent_first_singleton_create_policy` | POLICY_BLOCKED | [design](cases/content-models.md#home-t11b--test_concurrent_first_singleton_create_policy) |
| HOME-T12a | `test_slide_create_and_edit_persists_target_fields` | READY | [design](cases/content-models.md#home-t12a--test_slide_create_and_edit_persists_target_fields) |
| HOME-T12b | `test_slide_integer_order_and_caption_boundary` | READY | [design](cases/content-models.md#home-t12b--test_slide_integer_order_and_caption_boundary) |
| HOME-T12c | `test_slide_row_delete_is_repeatable` | READY | [design](cases/content-models.md#home-t12c--test_slide_row_delete_is_repeatable) |
| HOME-T13a | `test_admin_anonymous_and_nonstaff_are_denied` | READY | [design](cases/admin.md#home-t13a--test_admin_anonymous_and_nonstaff_are_denied) |
| HOME-T13b | `test_admin_individual_model_permissions_are_distinct` | READY | [design](cases/admin.md#home-t13b--test_admin_individual_model_permissions_are_distinct) |
| HOME-T13c | `test_admin_unsafe_requests_require_real_csrf` | READY | [design](cases/admin.md#home-t13c--test_admin_unsafe_requests_require_real_csrf) |
| HOME-T13d | `test_admin_superuser_can_read_home_models` | READY | [design](cases/admin.md#home-t13d--test_admin_superuser_can_read_home_models) |
| HOME-T14a | `test_admin_invalid_forms_do_not_run_singleton_hooks` | READY | [design](cases/admin.md#home-t14a--test_admin_invalid_forms_do_not_run_singleton_hooks) |
| HOME-T14b | `test_admin_add_creates_home_row_and_audit` | READY | [design](cases/admin.md#home-t14b--test_admin_add_creates_home_row_and_audit) |
| HOME-T14c | `test_admin_change_updates_home_row_and_audit` | READY | [design](cases/admin.md#home-t14c--test_admin_change_updates_home_row_and_audit) |
| HOME-T14d | `test_admin_delete_confirmation_and_cancel` | READY | [design](cases/admin.md#home-t14d--test_admin_delete_confirmation_and_cancel) |
| HOME-T14e | `test_admin_bulk_delete_removes_only_selected_rows` | READY | [design](cases/admin.md#home-t14e--test_admin_bulk_delete_removes_only_selected_rows) |
| HOME-T14f | `test_admin_stale_object_redirects_without_writes` | READY | [design](cases/admin.md#home-t14f--test_admin_stale_object_redirects_without_writes) |
| HOME-T14g | `test_admin_db_failure_rolls_back_singleton_and_audit` | READY | [design](cases/admin.md#home-t14g--test_admin_db_failure_rolls_back_singleton_and_audit) |
| HOME-T15a | `test_sortable_requires_post_and_change_permission` | READY | [design](cases/admin.md#home-t15a--test_sortable_requires_post_and_change_permission) |
| HOME-T15b | `test_sortable_updates_only_named_orders_and_repeats` | READY | [design](cases/admin.md#home-t15b--test_sortable_updates_only_named_orders_and_repeats) |
| HOME-T15c | `test_sortable_malformed_batches_are_not_partially_written` | READY | [design](cases/admin.md#home-t15c--test_sortable_malformed_batches_are_not_partially_written) |
| HOME-T15d | `test_sortable_empty_batch_is_noop` | READY | [design](cases/admin.md#home-t15d--test_sortable_empty_batch_is_noop) |
| HOME-T15e | `test_sortable_page_move_policy` | POLICY_BLOCKED | [design](cases/admin.md#home-t15e--test_sortable_page_move_policy) |
| HOME-T15f | `test_admin_new_slide_uses_maximum_plus_one` | READY | [design](cases/admin.md#home-t15f--test_admin_new_slide_uses_maximum_plus_one) |
| HOME-T15g | `test_sortable_errors_do_not_disclose_database_detail` | NEEDS_FIX | [design](cases/admin.md#home-t15g--test_sortable_errors_do_not_disclose_database_detail) |
| HOME-T15h | `test_sortable_noncanonical_order_policy` | POLICY_BLOCKED | [design](cases/admin.md#home-t15h--test_sortable_noncanonical_order_policy) |
| HOME-T16a | `test_first_seed_creates_exact_fictional_identities` | READY | [design](cases/seed-manifest.md#home-t16a--test_first_seed_creates_exact_fictional_identities) |
| HOME-T16b | `test_first_seed_creates_public_content_and_media` | READY | [design](cases/seed-manifest.md#home-t16b--test_first_seed_creates_public_content_and_media) |
| HOME-T16c | `test_first_seed_creates_alert_and_dashboard_manifest` | READY | [design](cases/seed-manifest.md#home-t16c--test_first_seed_creates_alert_and_dashboard_manifest) |
| HOME-T16d | `test_first_seed_populates_hours_and_votes` | READY | [design](cases/seed-manifest.md#home-t16d--test_first_seed_populates_hours_and_votes) |
| HOME-T16e | `test_first_seed_populates_newmember_marks` | READY | [design](cases/seed-manifest.md#home-t16e--test_first_seed_populates_newmember_marks) |
| HOME-T16f | `test_first_seed_populates_open_and_closed_polls` | READY | [design](cases/seed-manifest.md#home-t16f--test_first_seed_populates_open_and_closed_polls) |
| HOME-T17a | `test_repeat_seed_preserves_stable_row_identity` | READY | [design](cases/seed-manifest.md#home-t17a--test_repeat_seed_preserves_stable_row_identity) |
| HOME-T17b | `test_repeat_seed_preserves_unrelated_synthetic_records` | READY | [design](cases/seed-manifest.md#home-t17b--test_repeat_seed_preserves_unrelated_synthetic_records) |
| HOME-T17c | `test_member_field_role_and_photo_reset_policy` | POLICY_BLOCKED | [design](cases/seed-manifest.md#home-t17c--test_member_field_role_and_photo_reset_policy) |
| HOME-T17d | `test_seed_preserves_existing_home_rows` | READY | [design](cases/seed-manifest.md#home-t17d--test_seed_preserves_existing_home_rows) |
| HOME-T17e | `test_alert_and_dashboard_refresh_policy` | POLICY_BLOCKED | [design](cases/seed-manifest.md#home-t17e--test_alert_and_dashboard_refresh_policy) |
| HOME-T17f | `test_workflow_vote_and_date_refresh_policy` | POLICY_BLOCKED | [design](cases/seed-manifest.md#home-t17f--test_workflow_vote_and_date_refresh_policy) |
| HOME-T17g | `test_group_bound_renamed_member_recovery_policy` | POLICY_BLOCKED | [design](cases/seed-manifest.md#home-t17g--test_group_bound_renamed_member_recovery_policy) |
| HOME-T18a | `test_seed_non_demo_refusal_has_no_side_effects` | READY | [design](cases/seed-failures.md#home-t18a--test_seed_non_demo_refusal_has_no_side_effects) |
| HOME-T18b | `test_seed_refuses_credentialed_or_privileged_identity` | READY | [design](cases/seed-failures.md#home-t18b--test_seed_refuses_credentialed_or_privileged_identity) |
| HOME-T18c | `test_late_member_refusal_rolls_back_prior_member_writes` | READY | [design](cases/seed-failures.md#home-t18c--test_late_member_refusal_rolls_back_prior_member_writes) |
| HOME-T19a | `test_late_seed_db_failure_rolls_back_all_database_writes` | READY | [design](cases/seed-failures.md#home-t19a--test_late_seed_db_failure_rolls_back_all_database_writes) |
| HOME-T19b | `test_media_setup_failures_roll_back_prior_db_writes` | READY | [design](cases/seed-failures.md#home-t19b--test_media_setup_failures_roll_back_prior_db_writes) |
| HOME-T19c | `test_failed_seed_file_compensation_policy` | POLICY_BLOCKED | [design](cases/seed-failures.md#home-t19c--test_failed_seed_file_compensation_policy) |
| HOME-T19d | `test_seed_retry_after_partial_failure_finishes_once` | READY | [design](cases/seed-failures.md#home-t19d--test_seed_retry_after_partial_failure_finishes_once) |
| HOME-T20a | `test_ambiguous_group_or_username_collision_policy` | POLICY_BLOCKED | [design](cases/seed-failures.md#home-t20a--test_ambiguous_group_or_username_collision_policy) |
| HOME-T20b | `test_nonunique_seed_key_collision_policy` | POLICY_BLOCKED | [design](cases/seed-failures.md#home-t20b--test_nonunique_seed_key_collision_policy) |
| HOME-T20c | `test_direct_seed_helper_guard_and_atomicity_policy` | POLICY_BLOCKED | [design](cases/seed-failures.md#home-t20c--test_direct_seed_helper_guard_and_atomicity_policy) |
| HOME-T20d | `test_workflow_user_list_input_policy` | POLICY_BLOCKED | [design](cases/seed-failures.md#home-t20d--test_workflow_user_list_input_policy) |
| HOME-T21a | `test_seed_copies_only_public_source_asset` | READY | [design](cases/media-composition.md#home-t21a--test_seed_copies_only_public_source_asset) |
| HOME-T21b | `test_seed_interest_url_uses_local_demo_host` | READY | [design](cases/media-composition.md#home-t21b--test_seed_interest_url_uses_local_demo_host) |
| HOME-T21c | `test_seed_config_input_boundary_policy` | POLICY_BLOCKED | [design](cases/media-composition.md#home-t21c--test_seed_config_input_boundary_policy) |

## Original group mapping

No old group is dropped; scenario splits preserve the original parent ID.

| Original ID | New IDs |
| --- | --- |
| HOME-T01 | HOME-T01a, HOME-T01b, HOME-T01c, HOME-T01d, HOME-T01e, HOME-T01f |
| HOME-T02 | HOME-T02a, HOME-T02b, HOME-T02c, HOME-T02d |
| HOME-T03 | HOME-T03a, HOME-T03b, HOME-T03c, HOME-T03d, HOME-T03e, HOME-T03f |
| HOME-T04 | HOME-T04a, HOME-T04b, HOME-T04c, HOME-T04d |
| HOME-T05 | HOME-T05a, HOME-T05b, HOME-T05c, HOME-T05d |
| HOME-T06 | HOME-T06a, HOME-T06b, HOME-T06c, HOME-T06d, HOME-T06e |
| HOME-T07 | HOME-T07a, HOME-T07b, HOME-T07c, HOME-T07d |
| HOME-T08 | HOME-T08a, HOME-T08b, HOME-T08c |
| HOME-T09 | HOME-T09a, HOME-T09b, HOME-T09c, HOME-T09d, HOME-T09e |
| HOME-T10 | HOME-T10a, HOME-T10b, HOME-T10c, HOME-T10d, HOME-T10e |
| HOME-T11 | HOME-T11a, HOME-T11b |
| HOME-T12 | HOME-T12a, HOME-T12b, HOME-T12c |
| HOME-T13 | HOME-T13a, HOME-T13b, HOME-T13c, HOME-T13d |
| HOME-T14 | HOME-T14a, HOME-T14b, HOME-T14c, HOME-T14d, HOME-T14e, HOME-T14f, HOME-T14g |
| HOME-T15 | HOME-T15a, HOME-T15b, HOME-T15c, HOME-T15d, HOME-T15e, HOME-T15f, HOME-T15g, HOME-T15h |
| HOME-T16 | HOME-T16a, HOME-T16b, HOME-T16c, HOME-T16d, HOME-T16e, HOME-T16f |
| HOME-T17 | HOME-T17a, HOME-T17b, HOME-T17c, HOME-T17d, HOME-T17e, HOME-T17f, HOME-T17g |
| HOME-T18 | HOME-T18a, HOME-T18b, HOME-T18c |
| HOME-T19 | HOME-T19a, HOME-T19b, HOME-T19c, HOME-T19d |
| HOME-T20 | HOME-T20a, HOME-T20b, HOME-T20c, HOME-T20d |
| HOME-T21 | HOME-T21a, HOME-T21b, HOME-T21c |

## Inventory completeness

| Operation | Atomic cases |
| --- | --- |
| HOME-O01 | HOME-T03e, HOME-T04a, HOME-T04b, HOME-T04c, HOME-T04d, HOME-T05a, HOME-T05b, HOME-T05c, HOME-T05d, HOME-T01a, HOME-T01b |
| HOME-O02 | HOME-T05a, HOME-T05b, HOME-T05c, HOME-T01a, HOME-T01c, HOME-T02a, HOME-T02b |
| HOME-O03 | HOME-T05a, HOME-T05b, HOME-T05c, HOME-T01a |
| HOME-O04 | HOME-T03a, HOME-T03b, HOME-T03e, HOME-T04a, HOME-T04b, HOME-T04c, HOME-T04d, HOME-T05a, HOME-T05b, HOME-T05c, HOME-T05d, HOME-T01a, HOME-T01d |
| HOME-O05 | HOME-T06e, HOME-T03c, HOME-T03f, HOME-T05a, HOME-T05b, HOME-T05c, HOME-T01a, HOME-T01e, HOME-T02c, HOME-T02d |
| HOME-O06 | HOME-T14a, HOME-T14g, HOME-T08a, HOME-T08b, HOME-T08c, HOME-T09a, HOME-T09b, HOME-T09c, HOME-T09d, HOME-T09e, HOME-T10a, HOME-T10b, HOME-T10c, HOME-T10d, HOME-T10e, HOME-T11a, HOME-T11b |
| HOME-O07 | HOME-T14a, HOME-T14g, HOME-T08a, HOME-T08b, HOME-T08c, HOME-T09a, HOME-T09b, HOME-T09c, HOME-T09d, HOME-T09e, HOME-T10b, HOME-T10c, HOME-T10d, HOME-T11a, HOME-T11b |
| HOME-O08 | HOME-T14a, HOME-T09a, HOME-T09e, HOME-T10d, HOME-T10e, HOME-T12a, HOME-T12b, HOME-T12c |
| HOME-O09 | HOME-T13a, HOME-T13b, HOME-T13c, HOME-T13d, HOME-T14a, HOME-T14b, HOME-T14c, HOME-T14d, HOME-T14e, HOME-T14f, HOME-T14g, HOME-T10e |
| HOME-O10 | HOME-T13c, HOME-T15a, HOME-T15b, HOME-T15c, HOME-T15d, HOME-T15e, HOME-T15f, HOME-T15g, HOME-T15h |
| HOME-O11 | HOME-T21a, HOME-T21c, HOME-T18a, HOME-T18b, HOME-T18c, HOME-T19a, HOME-T19b, HOME-T19c, HOME-T19d, HOME-T16a, HOME-T16b, HOME-T17a, HOME-T17b |
| HOME-O12 | HOME-T18b, HOME-T18c, HOME-T20a, HOME-T20c, HOME-T16a, HOME-T17a, HOME-T17b, HOME-T17c, HOME-T17g |
| HOME-O13 | HOME-T21a, HOME-T21b, HOME-T21c, HOME-T19a, HOME-T19b, HOME-T19c, HOME-T19d, HOME-T20b, HOME-T20c, HOME-T16b, HOME-T16c, HOME-T17a, HOME-T17b, HOME-T17d, HOME-T17e |
| HOME-O14 | HOME-T19a, HOME-T19d, HOME-T20b, HOME-T20c, HOME-T20d, HOME-T16d, HOME-T16e, HOME-T16f, HOME-T17a, HOME-T17b, HOME-T17f |
| HOME-O15 | HOME-T06a, HOME-T06b, HOME-T06c, HOME-T06d, HOME-T06e, HOME-T07a, HOME-T07b |
| HOME-O16 | HOME-T07a, HOME-T07c, HOME-T07d, HOME-T21c, HOME-T03d, HOME-T01f |
