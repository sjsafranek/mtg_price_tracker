/*======================================================================*/
--  db_setup.sql
--   -- :mode=pl-sql:tabSize=3:indentSize=3:
--  2024-05-12T03:22:59.909Z
--  Purpose:
--  NOTE: must be connected as 'postgres' user or a superuser to start.
/*======================================================================*/

\set ON_ERROR_STOP on
set client_min_messages to 'warning';

-- add extentions

-- add function handlers
\i create_general_functions.sql

-- create tables
\i create_config_table.sql
\i create_tables.sql

-- create views
\i create_views.sql