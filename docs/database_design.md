# Phase 2 - Database Design

## Step 1 - Core Entities

1. User
2. Project
3. Sprint
4. Issue
5. MeetingNote
6. RiskReport
7. GitHubRepository

## User Entity

Attributes:

1. id
2. full_name
3. email
4. password_hash
5. role
6. created_at

## Project Entity

Attributes:

1. id
2. name
3. description
4. status
5. created_at
6. owner_id

## Sprint Entity

Attributes:

1. id
2. name
3. goal
4. start_date
5. end_date
6. status
7. project_id

## Issue Entity

Attributes:

1. id
2. title
3. description
4. issue_type
5. priority
6. status
7. created_at
8. sprint_id

## MeetingNote Entity

Attributes:

1. id
2. title
3. content
4. summary
5. created_at
6. project_id

## RiskReport Entity

Attributes:

1. id
2. risk_score
3. risk_level
4. prediction
5. reason
6. generated_at
7. project_id

## GitHubRepository Entity

Attributes:

1. id
2. repo_name
3. repo_url
4. description
5. owner_name
6. connected_at
7. project_id

# Entity Relationships

1. User → Project
   Relationship: One-to-Many

2. Project → Sprint
   Relationship: One-to-Many

3. Sprint → Issue
   Relationship: One-to-Many

4. Project → MeetingNote
   Relationship: One-to-Many

5. Project → RiskReport
   Relationship: One-to-Many

6. Project → GitHubRepository
   Relationship: One-to-One

# Primary Keys

User.id
Project.id
Sprint.id
Issue.id
MeetingNote.id
RiskReport.id
GitHubRepository.id

# Foreign Keys

Project.owner_id → User.id

Sprint.project_id → Project.id

Issue.sprint_id → Sprint.id

MeetingNote.project_id → Project.id

RiskReport.project_id → Project.id

GitHubRepository.project_id → Project.id