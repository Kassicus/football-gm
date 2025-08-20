# NFL GM Simulator - Project Planning Document

## Project Overview

### Vision Statement
Create a hyper-realistic, single-player NFL General Manager simulator that provides an authentic front-office experience with deep gameplay mechanics, realistic AI behavior, and comprehensive team management features.

### Target Audience
- NFL fans who want to experience the strategic depth of being an NFL GM
- Sports simulation enthusiasts
- Players who enjoy management games with realistic mechanics

### Technology Stack
- **Backend**: Python + FastAPI
- **Database**: SQLite
- **Frontend**: HTML/CSS + Minimal JavaScript
- **Additional**: HTMX for dynamic updates, Jinja2 templates

---

## Phase 1: Foundation & Core Systems

### 1.1 Database Schema & Data Models
**Priority**: Critical
**Estimated Time**: 2-3 weeks

#### Core Entities
- **Teams**: 32 NFL teams with historical data, colors, logos
- **Players**: Comprehensive player database with attributes
- **Positions**: All NFL positions with specific requirements
- **Contracts**: Salary structure, bonuses, cap hits
- **Draft Classes**: Historical and generated prospects
- **Game Results**: Season outcomes, statistics
- **Transactions**: Trades, signings, releases, claims

#### Key Relationships
- Player-Team associations with contract details
- Draft pick ownership and trading history
- Salary cap tracking and projections
- Performance statistics by season/game

### 1.2 Basic API Infrastructure
**Priority**: Critical
**Estimated Time**: 1-2 weeks

#### Core Endpoints
- Team management (GET, POST, PUT)
- Player operations (search, filter, update)
- Transaction logging
- Basic roster management
- Salary cap calculations

### 1.3 Fundamental Frontend Pages
**Priority**: Critical
**Estimated Time**: 2-3 weeks

#### Essential Views
- **Dashboard**: Team overview, recent news, upcoming events
- **Roster Management**: View/edit active roster and practice squad
- **Salary Cap**: Current cap situation, projections
- **Basic Navigation**: Clean, functional UI structure

---

## Phase 2: Player Management & Evaluation

### 2.1 Player Rating System
**Priority**: High
**Estimated Time**: 2-3 weeks

#### Attribute Categories
- **Physical**: Speed, strength, agility, size measurements
- **Mental**: Football IQ, leadership, work ethic
- **Technical**: Position-specific skills (accuracy, coverage, blocking)
- **Potential**: Development ceiling and trajectory
- **Injury Proneness**: Historical and risk factors

#### Dynamic Ratings
- Age-based progression/regression curves
- Performance-based adjustments
- Injury recovery impacts
- Training and coaching effects

### 2.2 Scouting System
**Priority**: High
**Estimated Time**: 3-4 weeks

#### College Scouting
- Regional scout assignments
- Scouting report accuracy levels
- Player "discovery" mechanics
- Combine and pro day integration

#### Pro Personnel Evaluation
- Opponent player analysis
- Free agent evaluation
- Trade target identification
- Injury and character flags

### 2.3 Player Development
**Priority**: Medium
**Estimated Time**: 2-3 weeks

#### Development Factors
- Age and experience curves
- Coaching staff quality impact
- Practice squad development
- Injury recovery and durability
- Character and work ethic influence

---

## Phase 3: Salary Cap & Contract Management

### 3.1 Comprehensive Salary Cap System
**Priority**: Critical
**Estimated Time**: 3-4 weeks

#### Cap Mechanics
- Annual cap calculations with carryover
- Dead money tracking and acceleration
- Restructure and extension options
- Performance and signing bonuses
- Rookie wage scale implementation

#### Contract Types
- Standard player contracts with guaranteed money
- Rookie contracts (1st round, other rounds)
- Veteran minimum and prove-it deals
- Franchise and transition tags
- Practice squad contracts

### 3.2 Contract Negotiation Engine
**Priority**: High
**Estimated Time**: 2-3 weeks

#### Negotiation Factors
- Market value calculations
- Player demands and priorities
- Agent relationships and difficulty
- Team loyalty and history
- Performance incentives structure

---

## Phase 4: Draft System

### 4.1 Draft Class Generation
**Priority**: High
**Estimated Time**: 2-3 weeks

#### Realistic Draft Classes
- Position-based scarcity modeling
- Talent distribution curves (weak/strong classes)
- Character and injury flag generation
- Combine performance simulation
- College production correlation

### 4.2 Draft Interface & Strategy
**Priority**: High
**Estimated Time**: 2-3 weeks

#### Draft Day Features
- Real-time draft board with rankings
- Trade proposal system during draft
- Scout recommendations and warnings
- Pick value chart integration
- Compensatory pick calculations

---

## Phase 5: AI & Simulation Engine

### 5.1 AI General Managers
**Priority**: Critical
**Estimated Time**: 4-5 weeks

#### AI Behavior Patterns
- Team-specific philosophies and strategies
- Realistic trade evaluation and proposals
- Draft strategy based on team needs
- Free agency approach and spending patterns
- Personnel decision consistency

#### Intelligence Levels
- Conservative vs. aggressive GM types
- Different evaluation priorities
- Mistake-prone vs. analytical approaches
- Short-term vs. long-term focus

### 5.2 Season Simulation
**Priority**: High
**Estimated Time**: 3-4 weeks

#### Game Simulation
- Realistic scoring and statistical outcomes
- Injury occurrence during games/practice
- Performance variance and consistency
- Weather and venue impacts
- Player development through gameplay

#### Season Progression
- Weekly injury reports and recovery
- Performance trends and hot streaks
- Playoff seeding and scenarios
- Award voting and recognition

---

## Phase 6: Advanced Features

### 6.1 Coaching Staff Management
**Priority**: Medium
**Estimated Time**: 2-3 weeks

#### Coaching Impact
- Scheme fit and player development
- Coordinator specialties and philosophies
- Head coach hiring and firing
- Staff continuity effects on player performance

### 6.2 Advanced Analytics
**Priority**: Medium
**Estimated Time**: 2-3 weeks

#### Modern NFL Metrics
- EPA (Expected Points Added) calculations
- DVOA-style efficiency ratings
- Next Gen Stats integration concepts
- Positional value and WAR calculations
- Predictive modeling for player performance

### 6.3 Media & Fan Relations
**Priority**: Low
**Estimated Time**: 2-3 weeks

#### Realistic Pressures
- Fan expectations and patience levels
- Media criticism and praise cycles
- Owner demands and job security
- Market size and revenue impacts
- Playoff drought consequences

---

## Phase 7: Polish & User Experience

### 7.1 Enhanced Interface
**Priority**: Medium
**Estimated Time**: 3-4 weeks

#### Quality of Life Features
- Advanced filtering and sorting options
- Customizable dashboard layouts
- Historical transaction and decision logging
- Export capabilities for analysis
- Keyboard shortcuts and power-user features

### 7.2 Tutorial & Onboarding
**Priority**: Medium
**Estimated Time**: 1-2 weeks

#### New User Experience
- Interactive tutorial covering basic concepts
- Guided first season with tips and explanations
- Help documentation and tooltips
- Difficulty settings for newcomers

---

## Technical Implementation Details

### Database Optimization
- **Indexing Strategy**: Optimize for common queries (player searches, cap calculations)
- **Data Integrity**: Foreign keys and constraints to maintain consistency
- **Performance**: Query optimization for complex salary cap scenarios
- **Backup Strategy**: Regular automated backups of game saves

### API Design Principles
- **RESTful Structure**: Consistent endpoint naming and HTTP methods
- **Error Handling**: Comprehensive error responses with user-friendly messages
- **Validation**: Input validation for all user actions
- **Documentation**: Auto-generated API documentation

### Frontend Architecture
- **Progressive Enhancement**: Core functionality works without JavaScript
- **Responsive Design**: Functional on various screen sizes
- **Accessibility**: Screen reader compatible, keyboard navigation
- **Performance**: Fast loading times for data-heavy pages

---

## Testing Strategy

### Unit Testing
- Database model validation
- Salary cap calculation accuracy
- Player rating and development algorithms
- AI decision-making logic

### Integration Testing
- API endpoint functionality
- Database transaction integrity
- Complex multi-step operations (trades, draft picks)

### User Acceptance Testing
- Realistic gameplay scenarios
- Performance under typical usage
- UI/UX validation with target users

---

## Success Metrics

### Core Functionality
- All salary cap scenarios calculate correctly
- AI makes realistic, varied decisions
- Player development follows logical patterns
- Draft classes provide engaging strategic choices

### User Experience
- New users can complete basic GM tasks within 30 minutes
- Experienced users can execute complex strategies efficiently
- Game maintains engagement over multiple seasons
- Performance remains smooth with large databases

---

## Risk Assessment & Mitigation

### Technical Risks
- **Database Performance**: Monitor query performance, optimize as needed
- **AI Complexity**: Start simple, iterate based on testing
- **Data Accuracy**: Validate against real NFL scenarios

### Scope Risks
- **Feature Creep**: Stick to planned phases, document future ideas
- **Perfectionism**: Set "good enough" standards for MVP features
- **Time Estimation**: Add 25% buffer to all estimates

### Mitigation Strategies
- Regular milestone reviews and scope adjustments
- Modular architecture allowing for easy feature additions
- Comprehensive testing at each phase completion

---

## Estimated Timeline

**Total Project Duration**: 12-15 months

- **Phase 1 (Foundation)**: Months 1-2
- **Phase 2 (Player Management)**: Months 2-4
- **Phase 3 (Salary Cap)**: Months 4-6
- **Phase 4 (Draft System)**: Months 6-8
- **Phase 5 (AI & Simulation)**: Months 8-11
- **Phase 6 (Advanced Features)**: Months 11-13
- **Phase 7 (Polish)**: Months 13-15

*Note: Timeline assumes part-time development (15-20 hours/week)*

---

## Next Steps

1. **Set up development environment** (Python, FastAPI, SQLite)
2. **Design initial database schema** for core entities
3. **Create basic project structure** and API skeleton
4. **Implement fundamental team and player models**
5. **Build basic roster management interface**

This document should be reviewed and updated regularly as the project evolves and new requirements emerge.