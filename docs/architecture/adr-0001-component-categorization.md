# ADR-0001: Component Categorization Methodology

## Status
Accepted

## Date
2025-01-27

## Context

The Warp Documentation Protocol requires systematic categorization of components across both local storage documentation (Twitch Docs) and repository documentation (Repos Docs). With 1,430+ services in the Twitch platform and 38+ components across 26 repositories in Surrentumlabs, we need consistent criteria to prioritize documentation efforts and resource allocation.

Without clear categorization methodology, teams cannot effectively:
- Prioritize critical infrastructure for monitoring and reliability
- Allocate development resources to high-impact systems
- Identify candidates for decommissioning or consolidation
- Plan system migrations and architectural changes

## Decision

We adopt a three-tier categorization system based on quantitative metrics and business impact:

### Essential Components
Components that are **business-critical** and meet one or more criteria:
- **High-Connectivity**: Services with 95+ dependents in dependency matrix
- **Revenue-Critical**: Direct impact on monetization (payments, subscriptions, commerce)
- **User-Facing Core**: Primary user experience (authentication, video streaming, chat)
- **Infrastructure Backbone**: Services required for platform operation

Examples: chat, video, web, commerce, identity, security, eventbus, common

### Semi-Essential Components  
Components that **support operations** but are not directly revenue-critical:
- **Developer Tooling**: CI/CD, testing frameworks, build systems
- **Monitoring & Observability**: Metrics, logging, alerting systems
- **Supporting Services**: Analytics, content management, discovery
- **Integration Points**: API gateways, service meshes, middleware

Examples: analytics, developer tools, content management, discovery services

### Non-Essential Components
Components with **limited dependencies** or specialized use:
- **Team Workspaces**: Individual contributor directories
- **Experimental Code**: Proof-of-concepts, prototypes
- **Legacy Systems**: Deprecated or graveyard components
- **Utilities**: Standalone tools with minimal integration

Examples: individual team directories, experimental features, utility scripts

## Categorization Methodology

### Quantitative Analysis
1. **Dependency Matrix Analysis**: Count incoming/outgoing dependencies
2. **Traffic Volume**: Analyze service-to-service communication patterns  
3. **Infrastructure Tags**: Identify components marked as "infra" type
4. **Fan-in/Fan-out Heuristics**: Services bridging multiple domains

### Qualitative Assessment
1. **Business Impact**: Revenue dependency and user experience impact
2. **Operational Criticality**: Required for platform availability
3. **Domain Integration**: Cross-domain bridge components
4. **Compliance Requirements**: Regulatory and security mandates

### Implementation Process
1. **Automated Scoring**: Use dependency matrix and service tags for initial classification
2. **Manual Review**: Business stakeholder review for borderline cases
3. **Regular Reassessment**: Quarterly review of category assignments
4. **Exception Handling**: Clear escalation path for disagreements

## Consequences

### Positive
- **Clear Prioritization**: Teams can focus resources on Essential components first
- **Risk Management**: Essential components get appropriate monitoring and reliability investment
- **Resource Optimization**: Non-Essential components identified for potential decommissioning
- **Architecture Planning**: Semi-Essential components provide clear upgrade/migration roadmap
- **Documentation Efficiency**: Prioritized approach to component documentation

### Negative
- **Maintenance Overhead**: Categories require periodic review and updates
- **Subjective Decisions**: Some components may fall in gray areas between categories
- **Stakeholder Alignment**: Requires consensus on business impact assessment
- **Tool Dependencies**: Categorization depends on accurate dependency matrix data

## Metrics and Validation

### Success Criteria
- All components assigned to categories within 30 days
- < 5% of components flagged for category reassignment per quarter
- Architecture decisions reference component categories
- Resource allocation aligns with category priorities

### Monitoring
- Track category distribution changes over time
- Monitor Essential component availability and performance
- Assess resource allocation alignment with categories
- Regular stakeholder feedback on category usefulness

## Implementation Notes

### Coverage.md Integration
- Add "category" column to all component tracking tables
- Update component YAML frontmatter with category field
- Generate category-based filtering and reporting views

### Component Card Enhancement
- Include category in Purpose section of all component cards
- Add category-based cross-references and relationships
- Document category-specific operational requirements

### Tooling Requirements
- Dependency matrix analysis tools
- Automated category validation scripts
- Category-based reporting dashboards
- Integration with monitoring and alerting systems

## Related Decisions
- [[adr-0002-disconnected-removal]] - Removal strategy for Non-Essential disconnected components
- Future ADRs on resource allocation and monitoring strategies

## Links
[[../../Twitch Docs/Index]] | [[../../Repos Docs/Index]] | [[../../Tasks]] | [[../../AGENTS]] | [[adr-0002-disconnected-removal]]
