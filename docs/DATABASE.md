# DATABASE.md

# RideVerse Database Design

Version: 1.0.0

Status: Planning

Database Engine

PostgreSQL

The RideVerse database is the single source of truth for all persistent game data.

Every important action must be stored securely.

The client must never directly access the database.

All communication happens through the backend.

---

# Database Goals

The database must be:

• Secure

• Scalable

• Fast

• Reliable

• Maintainable

• Expandable

• Highly Available

• Normalized

• AI Friendly

---

# Database Architecture

Client

↓

FastAPI Backend

↓

Service Layer

↓

Repository Layer

↓

PostgreSQL

↓

Backup System

Only the backend communicates with PostgreSQL.

---

# Database Rules

Never trust the client.

Never duplicate data.

Always use foreign keys.

Always use indexes.

Always use transactions.

Always validate data.

Never delete important data permanently.

Use soft delete whenever appropriate.

Every important action must be logged.

---

# Naming Convention

Tables

snake_case

Example

player_accounts

Columns

snake_case

Example

player_id

created_at

updated_at

Indexes

idx_table_column

Primary Keys

id

UUID

Foreign Keys

table_id

Example

player_id

vehicle_id

bike_id

car_id

---

# Common Columns

Every table should contain:

id

created_at

updated_at

created_by (optional)

updated_by (optional)

is_active

is_deleted

version

---

# Core Database Modules

The database is divided into modules.

Authentication

Players

Characters

Vehicles

Bikes

Cars

Weapons

Inventory

Economy

Garages

Properties

Businesses

Missions

Traffic

Police

NPCs

Marketplace

Friends

Clubs

Chat

Voice

Leaderboard

Achievements

Notifications

Settings

Analytics

Logs

Future Modules

---

# Authentication Module

Tables

player_accounts

player_sessions

refresh_tokens

email_verifications

password_resets

login_history

device_sessions

---

# Player Module

Tables

players

player_profiles

player_statistics

player_levels

player_settings

player_preferences

player_reputation

player_titles

---

# Character Module

Tables

characters

character_appearance

character_clothing

character_emotes

character_skills

character_progress

---

# Vehicle Module

Tables

vehicles

vehicle_ownership

vehicle_damage

vehicle_fuel

vehicle_service_history

vehicle_customization

vehicle_statistics

vehicle_history

---

# Bike Module

Tables

bikes

bike_engines

bike_suspension

bike_brakes

bike_wheels

bike_tires

bike_exhaust

bike_lights

bike_fuel_tanks

bike_seats

bike_handlebars

bike_decals

bike_paint

bike_upgrades

---

# Car Module

Tables

cars

car_engines

car_transmissions

car_suspension

car_brakes

car_wheels

car_tires

car_doors

car_lights

car_interior

car_exterior

car_paint

car_upgrades

---

# Database Standards

Every table must have:

Primary Key

Indexes

Foreign Keys

Created Timestamp

Updated Timestamp

Soft Delete

Version Number

Validation Rules

Relationships

---

# Security Rules

Passwords must never be stored in plain text.

Passwords must always be hashed.

Authentication tokens must be encrypted.

Sensitive information must never be exposed.

Player economy must always be server validated.

---

# AI Instructions

Every AI assistant must:

Read DATABASE.md before creating database code.

Never create tables outside this document.

Never duplicate tables.

Never remove columns without approval.

Always document schema changes.

Always create migrations.

---

# End of DATABASE.md Part 1

---

# DATABASE.md Part 2

# Player Database Schema

Version: 1.0.0

This section defines the player-related database structure.

---

# Table: player_accounts

Purpose

Stores account information.

Columns

id (UUID)

email

username

password_hash

email_verified

account_status

last_login

created_at

updated_at

is_deleted

---

# Table: players

Purpose

Stores the main player profile.

Columns

id (UUID)

account_id

display_name

level

experience

cash

bank_balance

reputation

health

stamina

energy

wanted_level

current_server

current_region

created_at

updated_at

---

# Table: player_statistics

Purpose

Stores gameplay statistics.

Columns

id

player_id

total_play_time

distance_walked

distance_driven

missions_completed

races_won

vehicles_owned

weapons_owned

money_earned

money_spent

highest_speed

highest_wheelie_score

daily_login_streak

created_at

updated_at

---

# Table: player_settings

Purpose

Stores player preferences.

Columns

id

player_id

language

graphics_quality

audio_volume

music_volume

voice_chat

notifications

control_layout

camera_mode

theme

created_at

updated_at

---

# Character Database

---

# Table: characters

Purpose

Stores character information.

Columns

id

player_id

first_name

last_name

gender

date_of_birth

height

weight

current_health

current_stamina

current_hunger

current_thirst

spawn_location

created_at

updated_at

---

# Table: character_appearance

Columns

id

character_id

hair_style

hair_color

eye_color

skin_tone

face_type

beard_style

tattoos

glasses

mask

helmet

created_at

updated_at

---

# Vehicle Database

---

# Table: vehicles

Purpose

Stores every owned vehicle.

Columns

id

player_id

vehicle_type

brand

model

year

vin

license_plate

purchase_price

current_value

fuel_level

health

engine_health

body_health

mileage

garage_id

created_at

updated_at

---

# Bike Database

---

# Table: bikes

Columns

id

vehicle_id

engine_level

turbo_level

exhaust_level

brake_level

wheel_level

tire_level

seat_level

paint_id

decal_id

headlight_level

horn_level

fuel_tank_level

suspension_level

chain_level

mirror_level

speedometer_level

created_at

updated_at

---

# Car Database

---

# Table: cars

Columns

id

vehicle_id

engine_level

transmission_level

brake_level

suspension_level

wheel_level

tire_level

paint_id

interior_level

spoiler_level

hood_level

roof_level

window_tint

nitrous_level

headlight_level

created_at

updated_at

---

# Relationships

player_accounts

↓

players

↓

characters

↓

vehicles

↓

bikes / cars

One account

↓

Many characters

One character

↓

Many vehicles

One vehicle

↓

One bike OR one car

---

# Required Indexes

email

username

player_id

character_id

vehicle_id

garage_id

license_plate

created_at

---

# Constraints

Email must be unique.

Username must be unique.

VIN must be unique.

License Plate must be unique.

Vehicle must belong to one player.

Bike must reference one vehicle.

Car must reference one vehicle.

---

# AI Instructions

Never duplicate player data.

Never duplicate vehicle ownership.

Always validate relationships.

Always create indexes.

Always use UUIDs.

Always use foreign keys.

Never break relationships.

---

# End of DATABASE.md Part 2

---

# DATABASE.md Part 3

# Inventory, Weapons, Economy, Properties & Business Database

Version: 1.0.0

This section defines the inventory, economy, property, garage and business database structure.

---

# Inventory Module

## Table: inventories

Purpose

Stores the main inventory for every player.

Columns

id

player_id

max_slots

used_slots

total_weight

created_at

updated_at

---

## Table: inventory_items

Purpose

Stores every item owned by a player.

Columns

id

inventory_id

item_id

item_name

item_type

quantity

rarity

weight

durability

stackable

equipped

created_at

updated_at

---

## Table: inventory_history

Purpose

Stores inventory transactions.

Columns

id

player_id

item_id

action

quantity

source

destination

created_at

---

# Weapon Module

## Table: weapons

Columns

id

weapon_name

weapon_type

damage

range

fire_rate

reload_speed

ammo_capacity

weight

purchase_price

sell_price

required_level

created_at

updated_at

---

## Table: player_weapons

Columns

id

player_id

weapon_id

ammo

durability

skin

equipped

created_at

updated_at

---

## Table: weapon_upgrades

Columns

id

weapon_id

scope

extended_magazine

silencer

laser

grip

skin

created_at

updated_at

---

# Economy Module

## Table: wallets

Columns

id

player_id

cash

bank_balance

last_transaction

created_at

updated_at

---

## Table: transactions

Columns

id

player_id

transaction_type

amount

balance_before

balance_after

reference

description

created_at

---

## Table: daily_rewards

Columns

id

player_id

day_number

reward_amount

claimed

claimed_at

created_at

---

# Garage Module

## Table: garages

Columns

id

player_id

garage_name

capacity

location

purchase_price

created_at

updated_at

---

## Table: garage_slots

Columns

id

garage_id

slot_number

vehicle_id

occupied

created_at

updated_at

---

# Property Module

## Table: properties

Columns

id

owner_id

property_type

property_name

city

address

purchase_price

current_value

level

storage_capacity

created_at

updated_at

---

# Business Module

## Table: businesses

Columns

id

owner_id

business_name

business_type

location

daily_income

employees

level

created_at

updated_at

---

## Table: business_income

Columns

id

business_id

income

expenses

net_profit

record_date

created_at

---

# Marketplace Module

## Table: marketplace_listings

Columns

id

seller_id

item_type

item_id

price

listing_status

created_at

updated_at

---

## Table: marketplace_sales

Columns

id

listing_id

buyer_id

seller_id

sale_price

sold_at

created_at

---

# Fuel System

## Table: fuel_stations

Columns

id

station_name

location

fuel_price

created_at

updated_at

---

## Table: fuel_history

Columns

id

vehicle_id

fuel_amount

price_paid

station_id

created_at

---

# Repair System

## Table: repair_history

Columns

id

vehicle_id

garage_id

repair_cost

repair_description

repaired_by

created_at

---

# Relationships

Player

↓

Inventory

↓

Items

↓

Weapons

↓

Marketplace

↓

Economy

↓

Garages

↓

Properties

↓

Businesses

---

# Required Indexes

player_id

inventory_id

weapon_id

garage_id

business_id

property_id

listing_id

vehicle_id

created_at

---

# Validation Rules

Inventory capacity must never be exceeded.

Wallet balance cannot become negative.

Marketplace sales must be validated by the backend.

Businesses must belong to one player.

Properties must belong to one player.

Garages must belong to one player.

Every transaction must be logged.

---

# AI Instructions

Never allow the client to modify:

Money

Inventory

Weapons

Businesses

Properties

Marketplace Listings

Vehicle Ownership

All economy operations must be validated by the backend.

Always record transaction history.

Always preserve data integrity.

---

# End of DATABASE.md Part 3

---

# DATABASE.md Part 4

# Missions, NPCs, Police, Traffic, Social Systems & Maintenance

Version: 1.0.0

This section defines the remaining database modules required for RideVerse.

These systems support gameplay, multiplayer, AI, analytics, and long-term maintenance.

---

# Mission Module

## Table: missions

Purpose

Stores all mission definitions.

Columns

id

mission_name

mission_type

difficulty

minimum_level

reward_cash

reward_experience

estimated_time

repeatable

created_at

updated_at

---

## Table: player_missions

Purpose

Stores player mission progress.

Columns

id

player_id

mission_id

status

progress

started_at

completed_at

reward_claimed

created_at

updated_at

---

## Table: mission_history

Columns

id

player_id

mission_id

completion_time

reward_cash

reward_experience

created_at

---

# NPC Module

## Table: npcs

Columns

id

npc_name

npc_type

location

dialogue_set

schedule_id

created_at

updated_at

---

## Table: npc_dialogues

Columns

id

npc_id

dialogue_key

dialogue_text

language

created_at

updated_at

---

# Police Module

## Table: police_records

Columns

id

player_id

wanted_level

total_arrests

total_fines

last_crime

created_at

updated_at

---

## Table: crime_history

Columns

id

player_id

crime_type

fine_amount

wanted_level

resolved

created_at

---

# Traffic Module

## Table: traffic_events

Columns

id

event_type

location

severity

created_at

updated_at

---

# Friends Module

## Table: friends

Columns

id

player_id

friend_player_id

status

created_at

updated_at

---

# Clubs Module

## Table: clubs

Columns

id

club_name

owner_id

description

member_limit

club_level

created_at

updated_at

---

## Table: club_members

Columns

id

club_id

player_id

role

joined_at

created_at

updated_at

---

# Chat Module

## Table: chat_channels

Columns

id

channel_name

channel_type

created_at

updated_at

---

## Table: chat_messages

Columns

id

channel_id

player_id

message

edited

deleted

created_at

updated_at

---

# Notification Module

## Table: notifications

Columns

id

player_id

title

message

notification_type

read

created_at

updated_at

---

# Achievement Module

## Table: achievements

Columns

id

achievement_name

description

reward

created_at

updated_at

---

## Table: player_achievements

Columns

id

player_id

achievement_id

unlocked_at

created_at

---

# Leaderboard Module

## Table: leaderboards

Columns

id

leaderboard_type

season

created_at

updated_at

---

## Table: leaderboard_entries

Columns

id

leaderboard_id

player_id

score

rank

updated_at

---

# Analytics Module

## Table: analytics_events

Columns

id

player_id

event_name

event_data

created_at

---

# Logging Module

## Table: audit_logs

Columns

id

actor_id

action

entity_type

entity_id

details

created_at

---

## Table: error_logs

Columns

id

service_name

error_message

stack_trace

severity

created_at

---

# Backup Strategy

Daily Incremental Backup

Weekly Full Backup

Monthly Archive Backup

Encrypted Backups

Automatic Restore Testing

Disaster Recovery Plan

---

# Database Maintenance

Schedule Regular VACUUM

Rebuild Indexes

Monitor Slow Queries

Archive Old Logs

Monitor Storage Usage

Monitor Replication Health

Monitor Connection Pool

Review Performance Metrics

---

# Relationships

Players

↓

Missions

↓

Rewards

↓

Economy

↓

Statistics

↓

Leaderboards

↓

Achievements

↓

Analytics

---

# Required Indexes

mission_id

npc_id

club_id

friend_player_id

leaderboard_id

notification_type

wanted_level

created_at

---

# Data Integrity Rules

Every relationship must use foreign keys.

Every important transaction must be atomic.

Every economy update must occur inside a database transaction.

Historical records must never be modified after creation.

Audit logs must be immutable.

---

# AI Instructions

Always create migrations for schema changes.

Never remove production tables without approval.

Never delete historical records.

Always preserve referential integrity.

Always optimize indexes after major schema updates.

Always document every schema change.

---

# DATABASE.md Completion Checklist

Before the database design is considered complete:

✓ All tables documented

✓ Relationships defined

✓ Indexes identified

✓ Constraints documented

✓ Security rules documented

✓ Backup strategy documented

✓ Maintenance procedures documented

✓ AI development rules documented

---

# End of DATABASE.md

Version 1.0.0