/**
 * Demo of Block Comment Breadcrumbs
 * Tests the enhanced parser with block style comments
 */

#include <stdio.h>

/*
 * AI_PHASE: ISSUE_TRACKER_INTEGRATION
 * AI_STATUS: IMPLEMENTED
 * AI_PATTERN: GITHUB_ISSUE_LINK_V1
 * AI_STRATEGY: Integrate breadcrumbs with GitHub issue tracking
 * AI_DETAILS: Added support for REF_TROUBLE_TICKET, REF_USER_FEEDBACK, REF_AUDIT_LOG
 * REF_GITHUB_ISSUE: #1
 * REF_TROUBLE_TICKET: TT-2025-001
 * REF_USER_FEEDBACK: feedback/user-request-001.txt
 * AI_CONTEXT: {
 *   "issue_tracker": "github",
 *   "auto_sync": true,
 *   "priority": "high"
 * }
 */
int init_issue_tracking(void) {
    printf("Issue tracking integration initialized\n");
    return 0;
}

// AI_PHASE: ERROR_RECOVERY
// AI_STATUS: FIXED
// AI_PATTERN: HUMAN_OVERRIDE_V1
// HUMAN_OVERRIDE: Manual fix applied by developer due to complex edge case
// PREVIOUS_IMPLEMENTATION_REF: commit abc123
// CORRECTION_REF: commit def456
// REF_AUDIT_LOG: logs/audit/fix-2025-10-09.log
// AI_CONTEXT: { "manual_intervention": true, "reason": "edge_case" }
int handle_edge_case(void) {
    printf("Edge case handled with human override\n");
    return 0;
}

/*
 * AI_PHASE: MULTI_LINE_SUPPORT
 * AI_STATUS: IMPLEMENTED
 * AI_PATTERN: BLOCK_COMMENT_PARSE_V1
 * AI_STRATEGY: Support both line and block comment styles
 * AI_NOTE: This demonstrates block comment parsing
 */
void test_block_comments(void) {
    printf("Block comment parsing works!\n");
}

int main(void) {
    printf("Enhanced Breadcrumb Parser Test\n");
    printf("================================\n\n");
    
    init_issue_tracking();
    handle_edge_case();
    test_block_comments();
    
    printf("\nAll tests passed!\n");
    return 0;
}
