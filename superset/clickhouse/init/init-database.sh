#!/usr/bin/env bash
sh -c "clickhouse-client -n <<-EOSQL
    CREATE DATABASE IF NOT EXISTS wba;
    CREATE TABLE IF NOT EXISTS wba.economic_policy_prediction(country_name String, time UInt32, gdp_growth_annual Float32) ENGINE = ReplacingMergeTree ORDER BY (country_name, time);
    CREATE TABLE IF NOT EXISTS wba.economic_data(country_name String, country_code String, indicator_name String, indicator_code String, time UInt32, value Float32) ENGINE = ReplacingMergeTree ORDER BY (country_name, indicator_name, time);
EOSQL"