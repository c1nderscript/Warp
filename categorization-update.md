# Component Categorization Analysis

Based on traffic volume, production usage, infrastructure tags, and dependency matrix analysis:

## Essential Components (Core Domains + High-Traffic Services)
- chat (domain) - Core messaging infrastructure, 151 services, massive fan-in/out
- commerce (domain) - Revenue-critical, 120 services, direct business impact
- identity (domain) - Authentication backbone, 76 services, required by all domains
- security (domain) - Platform security, 130+ services, critical infrastructure
- video (domain) - Platform core, 512 services, highest service count, streaming backbone
- web (domain) - User interface, 146 services, connects all domains
- chat-frontend (component) - UI for essential chat domain
- common - Shared infrastructure libraries, high-connectivity hub
- core-ui - Shared UI components, 95+ dependents per matrix
- twilight - API gateway, bridges all domains per dependency analysis
- spade - Analytics pipeline across all domains per architecture docs
- hygienic - Metrics collection used platform-wide per matrix
- player-core - Core video player, essential for video domain
- transcoder - Video transcoding, essential for streaming
- websocket-edge - Real-time connections, critical infrastructure
- eventbus - Event-driven architecture backbone
- edge - Content delivery edge infrastructure
- stats - Platform analytics and metrics
- subs - Subscription management (revenue-critical)
- security-cop - Security automation
- video-coreservices - Core video infrastructure
- video-monitoring - Video service monitoring

## Semi-Essential Components (DevOps + Monitoring + Supporting Services)
- content (domain) - Extensions and loyalty, lower traffic than core domains
- admin-services - Administrative tooling
- devtools - Developer productivity tools
- devinfra-chef - Infrastructure automation
- qa - Quality engineering
- qe - Quality engineering
- release - Release management
- systems - Systems management
- systems-terraform - Infrastructure as code
- terraform-modules - Infrastructure modules
- puppet-modules - Configuration management
- core-config-packages - Configuration infrastructure
- twitch-cdk - Development kit
- Xarth-Grafana - Monitoring infrastructure
- neteng - Network engineering
- nre - Network reliability engineering
- dcops - Data center operations
- vidops - Video operations
- infosec - Information security
- privacy - Privacy compliance
- slackbots - Internal tooling
- devhub - Developer portal
- devrel - Developer relations
- sdk - Software development kit
- video-puppet - Video infrastructure automation
- video-puppet-thirdparty - Third-party video tools
- video-tools - Video utility tools
- video-monitoring - Video monitoring

## Non-Essential Components (Individual Dirs + Legacy + Experiments)
- 3rdparty - Third-party code storage
- graveyard - Deprecated/archived code
- bootcamp - Training/onboarding materials
- gsoc - Google Summer of Code projects
- FETakehome - Interview/takehome projects
- blade-legacy - Legacy service
- stats-deprecated - Deprecated analytics
- flexotest - Test service for flexo
- All team directories (individual contributor workspaces)

## Team Directories (All Non-Essential)
All individual contributor and team-specific directories are Non-Essential:
CPE-Chef, CPE-Dev, CPE-Ops, Design, JChang, Twitch-IT, andaries, astith, benherr, bobbcarp, bryachar, danielnf, itsupport, jukenned, kdkly, kerbin, kevinbacon, kevipike, kkona, marqshee, mmdixon, mpaldhe, mponorof, ncaspar, product, rhys, royberg, rps, rrieblin, rwjblue, sean, timotyenorg, vidhurv, yilenpan

## Service Classification Logic:
- Essential: Core platform domains, high-connectivity services, revenue-critical, user-facing
- Semi-Essential: DevOps, CI/CD, monitoring, developer tools, supporting infrastructure
- Non-Essential: Personal directories, experiments, legacy, archived, training materials
