# PARLEYPRO case index

Source baseline: `7e25ac2f06b2d88a0220526771585f30df10c57a`.
Documentation-refinement baseline: `c8bbc4e`.

40 original groups expand to 114 independently named designs.
This is the frozen design index. Wave 2 execution of all 58 READY cases is recorded
in [README](README.md) and [case-map.json](case-map.json); 56 blocked designs remain unexecuted.
See [inventory and decisions](regression-spec.md) and the
[shared fixture contract](../../../docs/testing/fixture-contract.md).

## Primary readiness counts

| Status | Cases |
| --- | ---: |
| READY | 58 |
| NEEDS_FIX | 5 |
| POLICY_BLOCKED | 48 |
| INFRA_BLOCKED | 3 |

## New cases

| New ID | test_name | Primary status | Case file / anchor |
| --- | --- | --- | --- |
| PP-01a | `test_create_form_exposes_name_and_csrf` | READY | [creation.md](cases/creation.md#pp-01a) |
| PP-01b | `test_invalid_name_redisplay_escapes_html` | READY | [creation.md](cases/creation.md#pp-01b) |
| PP-02a | `test_create_saves_name_and_open_defaults` | READY | [creation.md](cases/creation.md#pp-02a) |
| PP-02b | `test_create_ignores_forged_model_fields` | READY | [creation.md](cases/creation.md#pp-02b) |
| PP-03a | `test_create_rejects_blank_name` | READY | [creation.md](cases/creation.md#pp-03a) |
| PP-03b | `test_create_rejects_name_over_max_length` | READY | [creation.md](cases/creation.md#pp-03b) |
| PP-03c | `test_create_accepts_name_length_boundaries_and_unicode` | READY | [creation.md](cases/creation.md#pp-03c) |
| PP-03d | `test_created_markup_name_is_escaped_on_page` | READY | [creation.md](cases/creation.md#pp-03d) |
| PP-04a | `test_anonymous_create_requires_login` | READY | [access.md](cases/access.md#pp-04a) |
| PP-04b | `test_create_denies_missing_profile_or_required_role` | READY | [access.md](cases/access.md#pp-04b) |
| PP-04c | `test_create_allows_exact_pair_and_extra_roles` | READY | [access.md](cases/access.md#pp-04c) |
| PP-04d | `test_superuser_without_profile_cannot_create_public_poll` | READY | [access.md](cases/access.md#pp-04d) |
| PP-05a | `test_create_rejects_missing_or_bad_csrf` | READY | [access.md](cases/access.md#pp-05a) |
| PP-05b | `test_cast_rejects_missing_or_bad_csrf` | READY | [access.md](cases/access.md#pp-05b) |
| PP-05c | `test_close_rejects_missing_or_bad_csrf` | READY | [access.md](cases/access.md#pp-05c) |
| PP-05d | `test_token_authenticated_create_succeeds` | READY | [access.md](cases/access.md#pp-05d) |
| PP-05e | `test_token_authenticated_cast_succeeds` | READY | [access.md](cases/access.md#pp-05e) |
| PP-05f | `test_token_authenticated_close_succeeds` | READY | [access.md](cases/access.md#pp-05f) |
| PP-05g | `test_live_post_obeys_csrf_while_get_remains_read_only` | POLICY_BLOCKED | [access.md](cases/access.md#pp-05g) |
| PP-06a | `test_create_while_another_poll_is_open` | POLICY_BLOCKED | [creation.md](cases/creation.md#pp-06a) |
| PP-06b | `test_replayed_create_has_explicit_retry_semantics` | POLICY_BLOCKED | [creation.md](cases/creation.md#pp-06b) |
| PP-07a | `test_cast_aye_creates_own_current_choice` | READY | [voting.md](cases/voting.md#pp-07a) |
| PP-07b | `test_cast_nay_creates_own_current_choice` | READY | [voting.md](cases/voting.md#pp-07b) |
| PP-07c | `test_change_choice_keeps_user_row_identity` | READY | [voting.md](cases/voting.md#pp-07c) |
| PP-07d | `test_repeat_identical_choice_is_idempotent_for_current_row` | READY | [voting.md](cases/voting.md#pp-07d) |
| PP-08a | `test_forged_target_fields_cannot_create_another_users_choice` | READY | [voting.md](cases/voting.md#pp-08a) |
| PP-08b | `test_forged_target_fields_cannot_redirect_existing_choice` | READY | [voting.md](cases/voting.md#pp-08b) |
| PP-09a | `test_dual_choice_keys_have_explicit_dispatch_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-09a) |
| PP-10a | `test_unknown_payload_with_absent_choice_has_explicit_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-10a) |
| PP-10b | `test_unknown_payload_with_existing_choice_has_explicit_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-10b) |
| PP-11a | `test_hidden_start_key_has_explicit_navigation_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-11a) |
| PP-11b | `test_start_key_mixed_with_actions_has_explicit_precedence` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-11b) |
| PP-12a | `test_end_plus_choice_keys_with_existing_actor_choice` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-12a) |
| PP-12b | `test_end_plus_choice_keys_with_absent_actor_choice` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-12b) |
| PP-13a | `test_cast_without_open_poll_has_explicit_transition_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-13a) |
| PP-14a | `test_multiple_open_poll_cast_has_explicit_target_identity` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-14a) |
| PP-14b | `test_equal_start_open_poll_selection_is_deterministic_by_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-14b) |
| PP-15a | `test_count_helper_excludes_nonchoice_literals` | READY | [voting.md](cases/voting.md#pp-15a) |
| PP-15b | `test_count_helper_respects_supplied_queryset` | READY | [voting.md](cases/voting.md#pp-15b) |
| PP-15c | `test_global_count_eligibility_has_explicit_role_and_orphan_policy` | POLICY_BLOCKED | [voting.md](cases/voting.md#pp-15c) |
| PP-16a | `test_close_saves_exact_totals_and_end_without_rewriting_metadata` | READY | [closure.md](cases/closure.md#pp-16a) |
| PP-16b | `test_close_reset_scope_for_nonvoters_and_corrupt_rows` | POLICY_BLOCKED | [closure.md](cases/closure.md#pp-16b) |
| PP-16c | `test_cross_creator_close_has_explicit_ownership_policy` | POLICY_BLOCKED | [closure.md](cases/closure.md#pp-16c) |
| PP-16d | `test_close_resets_current_rows_without_deleting_identity` | READY | [closure.md](cases/closure.md#pp-16d) |
| PP-17a | `test_active_nonexec_cannot_close_or_reset` | NEEDS_FIX | [access.md](cases/access.md#pp-17a) |
| PP-17b | `test_close_route_denies_actors_without_active` | READY | [access.md](cases/access.md#pp-17b) |
| PP-17c | `test_direct_close_helper_has_explicit_actor_boundary` | POLICY_BLOCKED | [access.md](cases/access.md#pp-17c) |
| PP-18a | `test_close_without_open_poll_is_noop` | READY | [closure.md](cases/closure.md#pp-18a) |
| PP-18b | `test_repeat_close_does_not_rewrite_single_closed_poll` | READY | [closure.md](cases/closure.md#pp-18b) |
| PP-19a | `test_repeated_close_cannot_silently_advance_to_other_open_poll` | POLICY_BLOCKED | [closure.md](cases/closure.md#pp-19a) |
| PP-20a | `test_close_tie_stores_equal_counts` | READY | [closure.md](cases/closure.md#pp-20a) |
| PP-20b | `test_close_zero_votes_stores_zero_and_renders_no_votes` | READY | [closure.md](cases/closure.md#pp-20b) |
| PP-20c | `test_tie_business_outcome_is_separate_from_admin_label` | POLICY_BLOCKED | [closure.md](cases/closure.md#pp-20c) |
| PP-21a | `test_count_query_failure_leaves_close_state_untouched` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-21a) |
| PP-21b | `test_poll_save_failure_before_write_leaves_choices_untouched` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-21b) |
| PP-22a | `test_reset_failure_has_atomic_or_recoverable_close_contract` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-22a) |
| PP-22b | `test_retry_after_partial_reset_failure_can_recover_without_recount_loss` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-22b) |
| PP-23a | `test_dual_choice_second_save_failure_has_defined_atomicity` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-23a) |
| PP-23b | `test_first_choice_save_failure_after_default_row_creation` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-23b) |
| PP-24a | `test_committed_vote_before_close_is_counted_on_postgresql` | INFRA_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-24a) |
| PP-24b | `test_vote_between_count_and_reset_has_defined_acceptance_boundary` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-24b) |
| PP-24c | `test_vote_after_reset_has_explicit_closed_poll_policy` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-24c) |
| PP-24d | `test_vote_change_between_count_queries_has_coherent_snapshot_policy` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-24d) |
| PP-25a | `test_two_closers_before_reset_preserve_first_finalized_result` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-25a) |
| PP-25b | `test_late_closer_cannot_overwrite_counts_after_first_reset` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-25b) |
| PP-25c | `test_concurrent_closers_with_multiple_opens_have_explicit_targets` | POLICY_BLOCKED | [failures-and-races.md](cases/failures-and-races.md#pp-25c) |
| PP-26a | `test_current_page_shows_open_poll_and_live_counts` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-26a) |
| PP-26b | `test_no_open_poll_page_remains_read_only_with_residual_choices` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-26b) |
| PP-26c | `test_active_actor_reads_another_creators_current_poll` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-26c) |
| PP-27a | `test_history_contains_closed_polls_in_descending_end_order` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-27a) |
| PP-27b | `test_empty_history_renders_no_polls_message` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-27b) |
| PP-27c | `test_history_formats_chicago_dst_without_changing_sort_order` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-27c) |
| PP-27d | `test_history_equal_end_times_have_explicit_tiebreak_policy` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-27d) |
| PP-27e | `test_history_nullable_aggregates_have_explicit_display_policy` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-27e) |
| PP-28a | `test_active_live_results_have_exact_integer_json_payload` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-28a) |
| PP-28b | `test_live_audience_outside_active_has_explicit_policy` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-28b) |
| PP-28c | `test_anonymous_live_results_redirect_without_counts` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-28c) |
| PP-28d | `test_live_zero_counts_are_integer_zeros` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-28d) |
| PP-28e | `test_live_counts_without_open_poll_have_explicit_scope_policy` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-28e) |
| PP-29a | `test_page_and_history_require_active_role` | READY | [access.md](cases/access.md#pp-29a) |
| PP-29b | `test_cast_denial_preserves_choices` | READY | [access.md](cases/access.md#pp-29b) |
| PP-29c | `test_active_and_extra_roles_can_read_and_cast` | READY | [access.md](cases/access.md#pp-29c) |
| PP-30a | `test_poll_routes_reverse_and_resolve_to_mounted_views` | READY | [reads-and-routes.md](cases/reads-and-routes.md#pp-30a) |
| PP-30b | `test_live_route_is_defined_once` | NEEDS_FIX | [reads-and-routes.md](cases/reads-and-routes.md#pp-30b) |
| PP-30c | `test_history_and_live_post_have_explicit_method_policy` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-30c) |
| PP-30d | `test_other_unsafe_methods_do_not_gain_mutation_semantics` | POLICY_BLOCKED | [reads-and-routes.md](cases/reads-and-routes.md#pp-30d) |
| PP-31a | `test_admin_result_icon_labels_and_safe_html` | READY | [admin.md](cases/admin.md#pp-31a) |
| PP-31b | `test_admin_result_column_sorts_by_yes_count` | READY | [admin.md](cases/admin.md#pp-31b) |
| PP-32a | `test_admin_nullable_counts_do_not_crash_or_silently_rewrite` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-32a) |
| PP-33a | `test_admin_denies_anonymous_and_nonstaff_domain_executive` | READY | [admin.md](cases/admin.md#pp-33a) |
| PP-33b | `test_admin_staff_without_model_permissions_cannot_read_or_write` | READY | [admin.md](cases/admin.md#pp-33b) |
| PP-33c | `test_admin_view_only_actor_cannot_post_change_or_delete` | READY | [admin.md](cases/admin.md#pp-33c) |
| PP-33d | `test_admin_granular_permissions_gate_corresponding_actions` | READY | [admin.md](cases/admin.md#pp-33d) |
| PP-33e | `test_inactive_staff_is_not_admitted_to_admin` | READY | [admin.md](cases/admin.md#pp-33e) |
| PP-34a | `test_admin_add_has_explicit_creator_and_history_policy` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-34a) |
| PP-34b | `test_admin_invalid_poll_form_preserves_database` | READY | [admin.md](cases/admin.md#pp-34b) |
| PP-34c | `test_admin_history_fields_have_explicit_edit_contract` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-34c) |
| PP-34d | `test_admin_single_delete_has_explicit_retention_contract` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-34d) |
| PP-34e | `test_admin_bulk_delete_has_explicit_confirmation_and_retention` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-34e) |
| PP-35a | `test_admin_close_cannot_bypass_count_reset_protocol` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-35a) |
| PP-35b | `test_admin_reopen_cannot_silently_overwrite_history` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-35b) |
| PP-35c | `test_admin_negative_counts_have_explicit_validation_policy` | POLICY_BLOCKED | [admin.md](cases/admin.md#pp-35c) |
| PP-36a | `test_current_choice_is_unique_per_nonnull_user` | READY | [model-boundaries.md](cases/model-boundaries.md#pp-36a) |
| PP-36b | `test_model_choice_validation_accepts_only_declared_nonnull_values` | READY | [model-boundaries.md](cases/model-boundaries.md#pp-36b) |
| PP-36c | `test_deleting_poll_creator_has_explicit_history_retention_policy` | POLICY_BLOCKED | [model-boundaries.md](cases/model-boundaries.md#pp-36c) |
| PP-37a | `test_close_response_does_not_present_closed_poll_as_current` | NEEDS_FIX | [closure.md](cases/closure.md#pp-37a) |
| PP-38a | `test_route_denial_returns_to_safe_same_origin_referer` | READY | [access.md](cases/access.md#pp-38a) |
| PP-38b | `test_route_denial_rejects_external_referer` | NEEDS_FIX | [access.md](cases/access.md#pp-38b) |
| PP-38c | `test_no_referer_denial_does_not_loop_back_to_denied_poll` | NEEDS_FIX | [access.md](cases/access.md#pp-38c) |
| PP-39a | `test_create_storage_failure_preserves_existing_state` | POLICY_BLOCKED | [creation.md](cases/creation.md#pp-39a) |
| PP-39b | `test_auto_add_uses_model_clock_after_view_clock` | READY | [creation.md](cases/creation.md#pp-39b) |
| PP-40a | `test_live_updates_from_initial_zero_render_without_missing_node_error` | INFRA_BLOCKED | [browser.md](cases/browser.md#pp-40a) |
| PP-40b | `test_no_open_poll_live_updates_have_explicit_ui_policy` | POLICY_BLOCKED | [browser.md](cases/browser.md#pp-40b) |
| PP-40c | `test_live_preference_persists_and_controls_fetch_cadence` | INFRA_BLOCKED | [browser.md](cases/browser.md#pp-40c) |

## Complete original-to-new mapping

Each original ID remains the Parent metadata of every listed child.
No old dense case paragraph remains alongside these replacements.

| Original parent | Replacement IDs |
| --- | --- |
| PP-01 | `PP-01a`, `PP-01b` |
| PP-02 | `PP-02a`, `PP-02b` |
| PP-03 | `PP-03a`, `PP-03b`, `PP-03c`, `PP-03d` |
| PP-04 | `PP-04a`, `PP-04b`, `PP-04c`, `PP-04d` |
| PP-05 | `PP-05a`, `PP-05b`, `PP-05c`, `PP-05d`, `PP-05e`, `PP-05f`, `PP-05g` |
| PP-06 | `PP-06a`, `PP-06b` |
| PP-07 | `PP-07a`, `PP-07b`, `PP-07c`, `PP-07d` |
| PP-08 | `PP-08a`, `PP-08b` |
| PP-09 | `PP-09a` |
| PP-10 | `PP-10a`, `PP-10b` |
| PP-11 | `PP-11a`, `PP-11b` |
| PP-12 | `PP-12a`, `PP-12b` |
| PP-13 | `PP-13a` |
| PP-14 | `PP-14a`, `PP-14b` |
| PP-15 | `PP-15a`, `PP-15b`, `PP-15c` |
| PP-16 | `PP-16a`, `PP-16b`, `PP-16c`, `PP-16d` |
| PP-17 | `PP-17a`, `PP-17b`, `PP-17c` |
| PP-18 | `PP-18a`, `PP-18b` |
| PP-19 | `PP-19a` |
| PP-20 | `PP-20a`, `PP-20b`, `PP-20c` |
| PP-21 | `PP-21a`, `PP-21b` |
| PP-22 | `PP-22a`, `PP-22b` |
| PP-23 | `PP-23a`, `PP-23b` |
| PP-24 | `PP-24a`, `PP-24b`, `PP-24c`, `PP-24d` |
| PP-25 | `PP-25a`, `PP-25b`, `PP-25c` |
| PP-26 | `PP-26a`, `PP-26b`, `PP-26c` |
| PP-27 | `PP-27a`, `PP-27b`, `PP-27c`, `PP-27d`, `PP-27e` |
| PP-28 | `PP-28a`, `PP-28b`, `PP-28c`, `PP-28d`, `PP-28e` |
| PP-29 | `PP-29a`, `PP-29b`, `PP-29c` |
| PP-30 | `PP-30a`, `PP-30b`, `PP-30c`, `PP-30d` |
| PP-31 | `PP-31a`, `PP-31b` |
| PP-32 | `PP-32a` |
| PP-33 | `PP-33a`, `PP-33b`, `PP-33c`, `PP-33d`, `PP-33e` |
| PP-34 | `PP-34a`, `PP-34b`, `PP-34c`, `PP-34d`, `PP-34e` |
| PP-35 | `PP-35a`, `PP-35b`, `PP-35c` |
| PP-36 | `PP-36a`, `PP-36b`, `PP-36c` |
| PP-37 | `PP-37a` |
| PP-38 | `PP-38a`, `PP-38b`, `PP-38c` |
| PP-39 | `PP-39a`, `PP-39b` |
| PP-40 | `PP-40a`, `PP-40b`, `PP-40c` |

## Workflow files

- [creation.md](cases/creation.md): 12 designs.
- [access.md](cases/access.md): 20 designs.
- [voting.md](cases/voting.md): 19 designs.
- [closure.md](cases/closure.md): 11 designs.
- [failures-and-races.md](cases/failures-and-races.md): 13 designs.
- [reads-and-routes.md](cases/reads-and-routes.md): 17 designs.
- [admin.md](cases/admin.md): 16 designs.
- [model-boundaries.md](cases/model-boundaries.md): 3 designs.
- [browser.md](cases/browser.md): 3 designs.
