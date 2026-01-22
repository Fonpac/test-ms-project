-- DROP SCHEMA pm;
CREATE SCHEMA pm AUTHORIZATION alpha;

-- Sequences
-- DROP SEQUENCE pm.import_batch_id_seq;
CREATE SEQUENCE pm.import_batch_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.import_batch_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.import_batch_id_seq TO alpha;

-- DROP SEQUENCE pm.project_id_seq;
CREATE SEQUENCE pm.project_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.project_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.project_id_seq TO alpha;

-- DROP SEQUENCE pm.task_id_seq;
CREATE SEQUENCE pm.task_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.task_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.task_id_seq TO alpha;

-- DROP SEQUENCE pm.resource_id_seq;
CREATE SEQUENCE pm.resource_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.resource_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.resource_id_seq TO alpha;

-- DROP SEQUENCE pm.assignment_id_seq;
CREATE SEQUENCE pm.assignment_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.assignment_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.assignment_id_seq TO alpha;

-- DROP SEQUENCE pm.task_dependency_id_seq;
CREATE SEQUENCE pm.task_dependency_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.task_dependency_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.task_dependency_id_seq TO alpha;

-- DROP SEQUENCE pm.calendar_id_seq;
CREATE SEQUENCE pm.calendar_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.calendar_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.calendar_id_seq TO alpha;

-- DROP SEQUENCE pm.calendar_weekday_id_seq;
CREATE SEQUENCE pm.calendar_weekday_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.calendar_weekday_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.calendar_weekday_id_seq TO alpha;

-- DROP SEQUENCE pm.calendar_working_time_id_seq;
CREATE SEQUENCE pm.calendar_working_time_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.calendar_working_time_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.calendar_working_time_id_seq TO alpha;

-- DROP SEQUENCE pm.calendar_exception_id_seq;
CREATE SEQUENCE pm.calendar_exception_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.calendar_exception_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.calendar_exception_id_seq TO alpha;

-- DROP SEQUENCE pm.assignment_timephased_planned_id_seq;
CREATE SEQUENCE pm.assignment_timephased_planned_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.assignment_timephased_planned_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.assignment_timephased_planned_id_seq TO alpha;

-- DROP SEQUENCE pm.assignment_timephased_complete_id_seq;
CREATE SEQUENCE pm.assignment_timephased_complete_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.assignment_timephased_complete_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.assignment_timephased_complete_id_seq TO alpha;

-- DROP SEQUENCE pm.baseline_id_seq;
CREATE SEQUENCE pm.baseline_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.baseline_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.baseline_id_seq TO alpha;

-- DROP SEQUENCE pm.task_baseline_id_seq;
CREATE SEQUENCE pm.task_baseline_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.task_baseline_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.task_baseline_id_seq TO alpha;

-- DROP SEQUENCE pm.resource_baseline_id_seq;
CREATE SEQUENCE pm.resource_baseline_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.resource_baseline_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.resource_baseline_id_seq TO alpha;

-- DROP SEQUENCE pm.user_access_project_id_seq;
CREATE SEQUENCE pm.user_access_project_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.user_access_project_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.user_access_project_id_seq TO alpha;

-- DROP SEQUENCE pm.client_user_group_access_project_id_seq;
CREATE SEQUENCE pm.client_user_group_access_project_id_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE;
ALTER SEQUENCE pm.client_user_group_access_project_id_seq OWNER TO alpha;
GRANT ALL ON SEQUENCE pm.client_user_group_access_project_id_seq TO alpha;

-- pm.project definition
-- Drop table
-- DROP TABLE pm.project;
CREATE TABLE pm.project (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    "name" varchar NOT NULL,
    start_date timestamp NULL,
    finish_date timestamp NULL,
    author varchar NULL,
    company varchar NULL,
    comments text NULL,
    creation_date timestamp NULL,
    last_saved timestamp NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT project_pk PRIMARY KEY (id)
);
CREATE INDEX project_name_index ON pm.project USING btree (name);
CREATE INDEX project_start_date_index ON pm.project USING btree (start_date);
CREATE INDEX project_finish_date_index ON pm.project USING btree (finish_date);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.project FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.project OWNER TO alpha;
GRANT ALL ON TABLE pm.project TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.project TO usage_on_tables;

-- pm.import_batch definition
-- Drop table
-- DROP TABLE pm.import_batch;
CREATE TABLE pm.import_batch (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    source_file varchar NULL,
    import_status varchar DEFAULT 'completed' NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT import_batch_pk PRIMARY KEY (id),
    CONSTRAINT import_batch_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX import_batch_project_id_index ON pm.import_batch USING btree (project_id);
CREATE INDEX import_batch_created_at_index ON pm.import_batch USING btree (created_at);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.import_batch FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.import_batch OWNER TO alpha;
GRANT ALL ON TABLE pm.import_batch TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.import_batch TO usage_on_tables;

-- pm.task definition
-- Drop table
-- DROP TABLE pm.task;
CREATE TABLE pm.task (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    external_id varchar NULL,
    "name" varchar NOT NULL,
    start_date timestamp NULL,
    finish_date timestamp NULL,
    duration numeric(10, 2) NULL,
    work numeric(10, 2) NULL,
    percent_complete int4 DEFAULT 0 NOT NULL,
    priority int4 NULL,
    notes text NULL,
    wbs varchar NULL,
    outline_level int4 DEFAULT 0 NOT NULL,
    milestone bool DEFAULT false NOT NULL,
    summary bool DEFAULT false NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT task_pk PRIMARY KEY (id),
    CONSTRAINT task_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT task_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX task_project_id_index ON pm.task USING btree (project_id);
CREATE INDEX task_import_batch_id_index ON pm.task USING btree (import_batch_id);
CREATE INDEX task_external_id_index ON pm.task USING btree (external_id);
CREATE INDEX task_start_date_index ON pm.task USING btree (start_date);
CREATE INDEX task_finish_date_index ON pm.task USING btree (finish_date);
CREATE INDEX task_wbs_index ON pm.task USING btree (wbs);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.task FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.task OWNER TO alpha;
GRANT ALL ON TABLE pm.task TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.task TO usage_on_tables;

-- pm.resource definition
-- Drop table
-- DROP TABLE pm.resource;
CREATE TABLE pm.resource (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    external_id varchar NULL,
    "name" varchar NOT NULL,
    email varchar NULL,
    "type" varchar NULL,
    "group" varchar NULL,
    max_units numeric(10, 2) NULL,
    standard_rate numeric(15, 2) NULL,
    cost numeric(15, 2) NULL,
    notes text NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT resource_pk PRIMARY KEY (id),
    CONSTRAINT resource_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT resource_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX resource_project_id_index ON pm.resource USING btree (project_id);
CREATE INDEX resource_import_batch_id_index ON pm.resource USING btree (import_batch_id);
CREATE INDEX resource_external_id_index ON pm.resource USING btree (external_id);
CREATE INDEX resource_name_index ON pm.resource USING btree (name);
CREATE INDEX resource_email_index ON pm.resource USING btree (email);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.resource FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.resource OWNER TO alpha;
GRANT ALL ON TABLE pm.resource TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.resource TO usage_on_tables;

-- pm.assignment definition
-- Drop table
-- DROP TABLE pm.assignment;
CREATE TABLE pm.assignment (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    task_id int4 NOT NULL,
    resource_id int4 NOT NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    start_date timestamp NULL,
    finish_date timestamp NULL,
    units numeric(10, 2) NULL,
    percent_complete int4 DEFAULT 0 NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT assignment_pk PRIMARY KEY (id),
    CONSTRAINT assignment_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT assignment_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id),
    CONSTRAINT assignment_task_id_fk FOREIGN KEY (task_id) REFERENCES pm.task(id),
    CONSTRAINT assignment_resource_id_fk FOREIGN KEY (resource_id) REFERENCES pm.resource(id)
);
CREATE INDEX assignment_project_id_index ON pm.assignment USING btree (project_id);
CREATE INDEX assignment_import_batch_id_index ON pm.assignment USING btree (import_batch_id);
CREATE INDEX assignment_task_id_index ON pm.assignment USING btree (task_id);
CREATE INDEX assignment_resource_id_index ON pm.assignment USING btree (resource_id);
CREATE UNIQUE INDEX assignment_unique_active ON pm.assignment USING btree (task_id, resource_id)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.assignment FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.assignment OWNER TO alpha;
GRANT ALL ON TABLE pm.assignment TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.assignment TO usage_on_tables;

-- pm.task_dependency definition
-- Drop table
-- DROP TABLE pm.task_dependency;
CREATE TABLE pm.task_dependency (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    predecessor_task_id int4 NOT NULL,
    successor_task_id int4 NOT NULL,
    dependency_type varchar NULL,
    lag numeric(10, 2) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT task_dependency_pk PRIMARY KEY (id),
    CONSTRAINT task_dependency_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT task_dependency_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id),
    CONSTRAINT task_dependency_predecessor_task_id_fk FOREIGN KEY (predecessor_task_id) REFERENCES pm.task(id),
    CONSTRAINT task_dependency_successor_task_id_fk FOREIGN KEY (successor_task_id) REFERENCES pm.task(id)
);
CREATE INDEX task_dependency_project_id_index ON pm.task_dependency USING btree (project_id);
CREATE INDEX task_dependency_import_batch_id_index ON pm.task_dependency USING btree (import_batch_id);
CREATE INDEX task_dependency_predecessor_task_id_index ON pm.task_dependency USING btree (predecessor_task_id);
CREATE INDEX task_dependency_successor_task_id_index ON pm.task_dependency USING btree (successor_task_id);
CREATE UNIQUE INDEX task_dependency_unique_active ON pm.task_dependency USING btree (predecessor_task_id, successor_task_id)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.task_dependency FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.task_dependency OWNER TO alpha;
GRANT ALL ON TABLE pm.task_dependency TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.task_dependency TO usage_on_tables;

-- pm.calendar definition
-- Drop table
-- DROP TABLE pm.calendar;
CREATE TABLE pm.calendar (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    external_id varchar NULL,
    "name" varchar NOT NULL,
    parent_calendar_id int4 NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT calendar_pk PRIMARY KEY (id),
    CONSTRAINT calendar_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT calendar_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id),
    CONSTRAINT calendar_parent_calendar_id_fk FOREIGN KEY (parent_calendar_id) REFERENCES pm.calendar(id)
);
CREATE INDEX calendar_project_id_index ON pm.calendar USING btree (project_id);
CREATE INDEX calendar_import_batch_id_index ON pm.calendar USING btree (import_batch_id);
CREATE INDEX calendar_external_id_index ON pm.calendar USING btree (external_id);
CREATE INDEX calendar_parent_calendar_id_index ON pm.calendar USING btree (parent_calendar_id);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.calendar FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.calendar OWNER TO alpha;
GRANT ALL ON TABLE pm.calendar TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.calendar TO usage_on_tables;

-- pm.calendar_weekday definition
-- Drop table
-- DROP TABLE pm.calendar_weekday;
CREATE TABLE pm.calendar_weekday (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    calendar_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    day_of_week int4 NOT NULL,
    working bool DEFAULT true NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT calendar_weekday_pk PRIMARY KEY (id),
    CONSTRAINT calendar_weekday_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id),
    CONSTRAINT calendar_weekday_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX calendar_weekday_calendar_id_index ON pm.calendar_weekday USING btree (calendar_id);
CREATE INDEX calendar_weekday_import_batch_id_index ON pm.calendar_weekday USING btree (import_batch_id);
CREATE UNIQUE INDEX calendar_weekday_unique_active ON pm.calendar_weekday USING btree (calendar_id, day_of_week)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.calendar_weekday FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.calendar_weekday OWNER TO alpha;
GRANT ALL ON TABLE pm.calendar_weekday TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.calendar_weekday TO usage_on_tables;

-- pm.calendar_working_time definition
-- Drop table
-- DROP TABLE pm.calendar_working_time;
CREATE TABLE pm.calendar_working_time (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    calendar_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    day_of_week int4 NOT NULL,
    start_time time NOT NULL,
    end_time time NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT calendar_working_time_pk PRIMARY KEY (id),
    CONSTRAINT calendar_working_time_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id),
    CONSTRAINT calendar_working_time_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX calendar_working_time_calendar_id_index ON pm.calendar_working_time USING btree (calendar_id);
CREATE INDEX calendar_working_time_import_batch_id_index ON pm.calendar_working_time USING btree (import_batch_id);
CREATE INDEX calendar_working_time_day_of_week_index ON pm.calendar_working_time USING btree (day_of_week);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.calendar_working_time FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.calendar_working_time OWNER TO alpha;
GRANT ALL ON TABLE pm.calendar_working_time TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.calendar_working_time TO usage_on_tables;

-- pm.calendar_exception definition
-- Drop table
-- DROP TABLE pm.calendar_exception;
CREATE TABLE pm.calendar_exception (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    calendar_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    exception_date date NOT NULL,
    working bool DEFAULT false NOT NULL,
    start_time time NULL,
    end_time time NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT calendar_exception_pk PRIMARY KEY (id),
    CONSTRAINT calendar_exception_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id),
    CONSTRAINT calendar_exception_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX calendar_exception_calendar_id_index ON pm.calendar_exception USING btree (calendar_id);
CREATE INDEX calendar_exception_import_batch_id_index ON pm.calendar_exception USING btree (import_batch_id);
CREATE INDEX calendar_exception_exception_date_index ON pm.calendar_exception USING btree (exception_date);
CREATE UNIQUE INDEX calendar_exception_unique_active ON pm.calendar_exception USING btree (calendar_id, exception_date)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.calendar_exception FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.calendar_exception OWNER TO alpha;
GRANT ALL ON TABLE pm.calendar_exception TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.calendar_exception TO usage_on_tables;

-- pm.assignment_timephased_planned definition
-- Drop table
-- DROP TABLE pm.assignment_timephased_planned;
CREATE TABLE pm.assignment_timephased_planned (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    assignment_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    period_start timestamp NOT NULL,
    period_end timestamp NOT NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    units numeric(10, 2) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT assignment_timephased_planned_pk PRIMARY KEY (id),
    CONSTRAINT assignment_timephased_planned_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES pm.assignment(id),
    CONSTRAINT assignment_timephased_planned_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX assignment_timephased_planned_assignment_id_index ON pm.assignment_timephased_planned USING btree (assignment_id);
CREATE INDEX assignment_timephased_planned_import_batch_id_index ON pm.assignment_timephased_planned USING btree (import_batch_id);
CREATE INDEX assignment_timephased_planned_period_start_index ON pm.assignment_timephased_planned USING btree (period_start);
CREATE INDEX assignment_timephased_planned_period_end_index ON pm.assignment_timephased_planned USING btree (period_end);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.assignment_timephased_planned FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.assignment_timephased_planned OWNER TO alpha;
GRANT ALL ON TABLE pm.assignment_timephased_planned TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.assignment_timephased_planned TO usage_on_tables;

-- pm.assignment_timephased_complete definition
-- Drop table
-- DROP TABLE pm.assignment_timephased_complete;
CREATE TABLE pm.assignment_timephased_complete (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    assignment_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    period_start timestamp NOT NULL,
    period_end timestamp NOT NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    units numeric(10, 2) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT assignment_timephased_complete_pk PRIMARY KEY (id),
    CONSTRAINT assignment_timephased_complete_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES pm.assignment(id),
    CONSTRAINT assignment_timephased_complete_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX assignment_timephased_complete_assignment_id_index ON pm.assignment_timephased_complete USING btree (assignment_id);
CREATE INDEX assignment_timephased_complete_import_batch_id_index ON pm.assignment_timephased_complete USING btree (import_batch_id);
CREATE INDEX assignment_timephased_complete_period_start_index ON pm.assignment_timephased_complete USING btree (period_start);
CREATE INDEX assignment_timephased_complete_period_end_index ON pm.assignment_timephased_complete USING btree (period_end);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.assignment_timephased_complete FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.assignment_timephased_complete OWNER TO alpha;
GRANT ALL ON TABLE pm.assignment_timephased_complete TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.assignment_timephased_complete TO usage_on_tables;

-- pm.baseline definition
-- Drop table
-- DROP TABLE pm.baseline;
CREATE TABLE pm.baseline (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    "name" varchar NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT baseline_pk PRIMARY KEY (id),
    CONSTRAINT baseline_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT baseline_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX baseline_project_id_index ON pm.baseline USING btree (project_id);
CREATE INDEX baseline_import_batch_id_index ON pm.baseline USING btree (import_batch_id);
CREATE INDEX baseline_name_index ON pm.baseline USING btree (name);
CREATE UNIQUE INDEX baseline_unique_active ON pm.baseline USING btree (project_id, name)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.baseline FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.baseline OWNER TO alpha;
GRANT ALL ON TABLE pm.baseline TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.baseline TO usage_on_tables;

-- pm.task_baseline definition
-- Drop table
-- DROP TABLE pm.task_baseline;
CREATE TABLE pm.task_baseline (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    baseline_id int4 NOT NULL,
    task_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    start_date timestamp NULL,
    finish_date timestamp NULL,
    duration numeric(10, 2) NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT task_baseline_pk PRIMARY KEY (id),
    CONSTRAINT task_baseline_baseline_id_fk FOREIGN KEY (baseline_id) REFERENCES pm.baseline(id),
    CONSTRAINT task_baseline_task_id_fk FOREIGN KEY (task_id) REFERENCES pm.task(id),
    CONSTRAINT task_baseline_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX task_baseline_baseline_id_index ON pm.task_baseline USING btree (baseline_id);
CREATE INDEX task_baseline_task_id_index ON pm.task_baseline USING btree (task_id);
CREATE INDEX task_baseline_import_batch_id_index ON pm.task_baseline USING btree (import_batch_id);
CREATE UNIQUE INDEX task_baseline_unique_active ON pm.task_baseline USING btree (baseline_id, task_id)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.task_baseline FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.task_baseline OWNER TO alpha;
GRANT ALL ON TABLE pm.task_baseline TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.task_baseline TO usage_on_tables;

-- pm.resource_baseline definition
-- Drop table
-- DROP TABLE pm.resource_baseline;
CREATE TABLE pm.resource_baseline (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    baseline_id int4 NOT NULL,
    resource_id int4 NOT NULL,
    import_batch_id int4 NOT NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT resource_baseline_pk PRIMARY KEY (id),
    CONSTRAINT resource_baseline_baseline_id_fk FOREIGN KEY (baseline_id) REFERENCES pm.baseline(id),
    CONSTRAINT resource_baseline_resource_id_fk FOREIGN KEY (resource_id) REFERENCES pm.resource(id),
    CONSTRAINT resource_baseline_import_batch_id_fk FOREIGN KEY (import_batch_id) REFERENCES pm.import_batch(id)
);
CREATE INDEX resource_baseline_baseline_id_index ON pm.resource_baseline USING btree (baseline_id);
CREATE INDEX resource_baseline_resource_id_index ON pm.resource_baseline USING btree (resource_id);
CREATE INDEX resource_baseline_import_batch_id_index ON pm.resource_baseline USING btree (import_batch_id);
CREATE UNIQUE INDEX resource_baseline_unique_active ON pm.resource_baseline USING btree (baseline_id, resource_id)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.resource_baseline FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.resource_baseline OWNER TO alpha;
GRANT ALL ON TABLE pm.resource_baseline TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.resource_baseline TO usage_on_tables;

-- pm.user_access_project definition
-- Drop table
-- DROP TABLE pm.user_access_project;
CREATE TABLE pm.user_access_project (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    user_id int4 NOT NULL,
    project_id int4 NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    created_by int4 NOT NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT user_access_project_pk PRIMARY KEY (id),
    CONSTRAINT user_access_project_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX user_access_project_project_id_index ON pm.user_access_project USING btree (project_id);
CREATE INDEX user_access_project_user_id_index ON pm.user_access_project USING btree (user_id);
CREATE UNIQUE INDEX user_access_project_unique_active ON pm.user_access_project USING btree (project_id, user_id)
WHERE (deleted_at IS NULL);
-- Permissions
ALTER TABLE pm.user_access_project OWNER TO alpha;
GRANT ALL ON TABLE pm.user_access_project TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.user_access_project TO usage_on_tables;

-- pm.client_user_group_access_project definition
-- Drop table
-- DROP TABLE pm.client_user_group_access_project;
CREATE TABLE pm.client_user_group_access_project (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    user_group_id int4 NOT NULL,
    project_id int4 NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    created_by int4 NOT NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT client_user_group_access_project_pk PRIMARY KEY (id),
    CONSTRAINT client_user_group_access_project_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX client_user_group_access_project_project_id_index ON pm.client_user_group_access_project USING btree (project_id);
CREATE INDEX client_user_group_access_project_user_group_id_index ON pm.client_user_group_access_project USING btree (user_group_id);
CREATE UNIQUE INDEX client_user_group_access_project_unique_active ON pm.client_user_group_access_project USING btree (project_id, user_group_id)
WHERE (deleted_at IS NULL);
-- Permissions
ALTER TABLE pm.client_user_group_access_project OWNER TO alpha;
GRANT ALL ON TABLE pm.client_user_group_access_project TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.client_user_group_access_project TO usage_on_tables;

-- Permissions
GRANT ALL ON SCHEMA pm TO alpha;
GRANT USAGE ON SCHEMA pm TO usage_on_tables;
ALTER DEFAULT PRIVILEGES FOR ROLE alpha IN SCHEMA pm
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLES TO usage_on_tables;

-- ============================================================================
-- FUNÇÕES PARA IMPORTAÇÃO DE DADOS
-- ============================================================================

-- Função para criar ou obter projeto existente
CREATE OR REPLACE FUNCTION pm.upsert_project(
    p_name varchar,
    p_start_date timestamp DEFAULT NULL,
    p_finish_date timestamp DEFAULT NULL,
    p_author varchar DEFAULT NULL,
    p_company varchar DEFAULT NULL,
    p_comments text DEFAULT NULL,
    p_creation_date timestamp DEFAULT NULL,
    p_last_saved timestamp DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT project_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    -- Tenta encontrar projeto existente não deletado com o mesmo nome
    SELECT id INTO project_id
    FROM pm.project
    WHERE name = p_name AND deleted_at IS NULL
    LIMIT 1;
    
    IF project_id IS NULL THEN
        -- Cria novo projeto
        INSERT INTO pm.project (
            name, start_date, finish_date, author, company, comments,
            creation_date, last_saved, created_by
        ) VALUES (
            p_name, p_start_date, p_finish_date, p_author, p_company, p_comments,
            p_creation_date, p_last_saved, p_created_by
        ) RETURNING id INTO project_id;
    ELSE
        -- Atualiza projeto existente
        UPDATE pm.project SET
            start_date = COALESCE(p_start_date, start_date),
            finish_date = COALESCE(p_finish_date, finish_date),
            author = COALESCE(p_author, author),
            company = COALESCE(p_company, company),
            comments = COALESCE(p_comments, comments),
            creation_date = COALESCE(p_creation_date, creation_date),
            last_saved = COALESCE(p_last_saved, last_saved),
            updated_at = CURRENT_TIMESTAMP,
            updated_by = p_created_by
        WHERE id = project_id;
    END IF;
END;
$$;

-- Função para criar import_batch
CREATE OR REPLACE FUNCTION pm.create_import_batch(
    p_project_id int4,
    p_source_file varchar DEFAULT NULL,
    p_import_status varchar DEFAULT 'completed',
    p_created_by int4 DEFAULT 1,
    OUT import_batch_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.import_batch (
        project_id, source_file, import_status, created_by
    ) VALUES (
        p_project_id, p_source_file, p_import_status, p_created_by
    ) RETURNING id INTO import_batch_id;
END;
$$;

-- Função para inserir tarefa
CREATE OR REPLACE FUNCTION pm.insert_task(
    p_project_id int4,
    p_import_batch_id int4,
    p_external_id varchar DEFAULT NULL,
    p_name varchar,
    p_start_date timestamp DEFAULT NULL,
    p_finish_date timestamp DEFAULT NULL,
    p_duration numeric DEFAULT NULL,
    p_work numeric DEFAULT NULL,
    p_percent_complete int4 DEFAULT 0,
    p_priority int4 DEFAULT NULL,
    p_notes text DEFAULT NULL,
    p_wbs varchar DEFAULT NULL,
    p_outline_level int4 DEFAULT 0,
    p_milestone bool DEFAULT false,
    p_summary bool DEFAULT false,
    p_created_by int4 DEFAULT 1,
    OUT task_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.task (
        project_id, import_batch_id, external_id, name, start_date, finish_date,
        duration, work, percent_complete, priority, notes, wbs, outline_level,
        milestone, summary, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_external_id, p_name, p_start_date, p_finish_date,
        p_duration, p_work, p_percent_complete, p_priority, p_notes, p_wbs, p_outline_level,
        p_milestone, p_summary, p_created_by
    ) RETURNING id INTO task_id;
END;
$$;

-- Função para inserir recurso
CREATE OR REPLACE FUNCTION pm.insert_resource(
    p_project_id int4,
    p_import_batch_id int4,
    p_external_id varchar DEFAULT NULL,
    p_name varchar,
    p_email varchar DEFAULT NULL,
    p_type varchar DEFAULT NULL,
    p_group varchar DEFAULT NULL,
    p_max_units numeric DEFAULT NULL,
    p_standard_rate numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_notes text DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT resource_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.resource (
        project_id, import_batch_id, external_id, name, email, type, "group",
        max_units, standard_rate, cost, notes, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_external_id, p_name, p_email, p_type, p_group,
        p_max_units, p_standard_rate, p_cost, p_notes, p_created_by
    ) RETURNING id INTO resource_id;
END;
$$;

-- Função para inserir atribuição
CREATE OR REPLACE FUNCTION pm.insert_assignment(
    p_project_id int4,
    p_import_batch_id int4,
    p_task_id int4,
    p_resource_id int4,
    p_work numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_start_date timestamp DEFAULT NULL,
    p_finish_date timestamp DEFAULT NULL,
    p_units numeric DEFAULT NULL,
    p_percent_complete int4 DEFAULT 0,
    p_created_by int4 DEFAULT 1,
    OUT assignment_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.assignment (
        project_id, import_batch_id, task_id, resource_id, work, cost,
        start_date, finish_date, units, percent_complete, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_task_id, p_resource_id, p_work, p_cost,
        p_start_date, p_finish_date, p_units, p_percent_complete, p_created_by
    ) RETURNING id INTO assignment_id;
END;
$$;

-- Função para inserir dependência de tarefa
CREATE OR REPLACE FUNCTION pm.insert_task_dependency(
    p_project_id int4,
    p_import_batch_id int4,
    p_predecessor_task_id int4,
    p_successor_task_id int4,
    p_dependency_type varchar DEFAULT NULL,
    p_lag numeric DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT dependency_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.task_dependency (
        project_id, import_batch_id, predecessor_task_id, successor_task_id,
        dependency_type, lag, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_predecessor_task_id, p_successor_task_id,
        p_dependency_type, p_lag, p_created_by
    ) RETURNING id INTO dependency_id;
END;
$$;

-- Função para inserir calendário
CREATE OR REPLACE FUNCTION pm.insert_calendar(
    p_project_id int4,
    p_import_batch_id int4,
    p_external_id varchar DEFAULT NULL,
    p_name varchar,
    p_parent_calendar_id int4 DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT calendar_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.calendar (
        project_id, import_batch_id, external_id, name, parent_calendar_id, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_external_id, p_name, p_parent_calendar_id, p_created_by
    ) RETURNING id INTO calendar_id;
END;
$$;

-- Função para inserir dia da semana do calendário
CREATE OR REPLACE FUNCTION pm.insert_calendar_weekday(
    p_calendar_id int4,
    p_import_batch_id int4,
    p_day_of_week int4,
    p_working bool DEFAULT true,
    p_created_by int4 DEFAULT 1,
    OUT weekday_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.calendar_weekday (
        calendar_id, import_batch_id, day_of_week, working, created_by
    ) VALUES (
        p_calendar_id, p_import_batch_id, p_day_of_week, p_working, p_created_by
    ) RETURNING id INTO weekday_id;
END;
$$;

-- Função para inserir horário de trabalho do calendário
CREATE OR REPLACE FUNCTION pm.insert_calendar_working_time(
    p_calendar_id int4,
    p_import_batch_id int4,
    p_day_of_week int4,
    p_start_time time,
    p_end_time time,
    p_created_by int4 DEFAULT 1,
    OUT working_time_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.calendar_working_time (
        calendar_id, import_batch_id, day_of_week, start_time, end_time, created_by
    ) VALUES (
        p_calendar_id, p_import_batch_id, p_day_of_week, p_start_time, p_end_time, p_created_by
    ) RETURNING id INTO working_time_id;
END;
$$;

-- Função para inserir exceção do calendário
CREATE OR REPLACE FUNCTION pm.insert_calendar_exception(
    p_calendar_id int4,
    p_import_batch_id int4,
    p_exception_date date,
    p_working bool DEFAULT false,
    p_start_time time DEFAULT NULL,
    p_end_time time DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT exception_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.calendar_exception (
        calendar_id, import_batch_id, exception_date, working, start_time, end_time, created_by
    ) VALUES (
        p_calendar_id, p_import_batch_id, p_exception_date, p_working, p_start_time, p_end_time, p_created_by
    ) RETURNING id INTO exception_id;
END;
$$;

-- Função para inserir dados timephased planejados
CREATE OR REPLACE FUNCTION pm.insert_assignment_timephased_planned(
    p_assignment_id int4,
    p_import_batch_id int4,
    p_period_start timestamp,
    p_period_end timestamp,
    p_work numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_units numeric DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT timephased_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.assignment_timephased_planned (
        assignment_id, import_batch_id, period_start, period_end, work, cost, units, created_by
    ) VALUES (
        p_assignment_id, p_import_batch_id, p_period_start, p_period_end, p_work, p_cost, p_units, p_created_by
    ) RETURNING id INTO timephased_id;
END;
$$;

-- Função para inserir dados timephased completos
CREATE OR REPLACE FUNCTION pm.insert_assignment_timephased_complete(
    p_assignment_id int4,
    p_import_batch_id int4,
    p_period_start timestamp,
    p_period_end timestamp,
    p_work numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_units numeric DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT timephased_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.assignment_timephased_complete (
        assignment_id, import_batch_id, period_start, period_end, work, cost, units, created_by
    ) VALUES (
        p_assignment_id, p_import_batch_id, p_period_start, p_period_end, p_work, p_cost, p_units, p_created_by
    ) RETURNING id INTO timephased_id;
END;
$$;

-- Função para inserir baseline
CREATE OR REPLACE FUNCTION pm.insert_baseline(
    p_project_id int4,
    p_import_batch_id int4,
    p_name varchar,
    p_created_by int4 DEFAULT 1,
    OUT baseline_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.baseline (
        project_id, import_batch_id, name, created_by
    ) VALUES (
        p_project_id, p_import_batch_id, p_name, p_created_by
    ) RETURNING id INTO baseline_id;
END;
$$;

-- Função para inserir baseline de tarefa
CREATE OR REPLACE FUNCTION pm.insert_task_baseline(
    p_baseline_id int4,
    p_task_id int4,
    p_import_batch_id int4,
    p_start_date timestamp DEFAULT NULL,
    p_finish_date timestamp DEFAULT NULL,
    p_duration numeric DEFAULT NULL,
    p_work numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT task_baseline_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.task_baseline (
        baseline_id, task_id, import_batch_id, start_date, finish_date,
        duration, work, cost, created_by
    ) VALUES (
        p_baseline_id, p_task_id, p_import_batch_id, p_start_date, p_finish_date,
        p_duration, p_work, p_cost, p_created_by
    ) RETURNING id INTO task_baseline_id;
END;
$$;

-- Função para inserir baseline de recurso
CREATE OR REPLACE FUNCTION pm.insert_resource_baseline(
    p_baseline_id int4,
    p_resource_id int4,
    p_import_batch_id int4,
    p_work numeric DEFAULT NULL,
    p_cost numeric DEFAULT NULL,
    p_created_by int4 DEFAULT 1,
    OUT resource_baseline_id int4
) RETURNS int4
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO pm.resource_baseline (
        baseline_id, resource_id, import_batch_id, work, cost, created_by
    ) VALUES (
        p_baseline_id, p_resource_id, p_import_batch_id, p_work, p_cost, p_created_by
    ) RETURNING id INTO resource_baseline_id;
END;
$$;

-- Função helper para buscar task_id por external_id
CREATE OR REPLACE FUNCTION pm.get_task_id_by_external_id(
    p_project_id int4,
    p_external_id varchar,
    p_import_batch_id int4 DEFAULT NULL
) RETURNS int4
LANGUAGE plpgsql
AS $$
DECLARE
    v_task_id int4;
BEGIN
    SELECT id INTO v_task_id
    FROM pm.task
    WHERE project_id = p_project_id
      AND external_id = p_external_id
      AND deleted_at IS NULL
      AND (p_import_batch_id IS NULL OR import_batch_id = p_import_batch_id)
    ORDER BY import_batch_id DESC
    LIMIT 1;
    
    RETURN v_task_id;
END;
$$;

-- Função helper para buscar resource_id por external_id
CREATE OR REPLACE FUNCTION pm.get_resource_id_by_external_id(
    p_project_id int4,
    p_external_id varchar,
    p_import_batch_id int4 DEFAULT NULL
) RETURNS int4
LANGUAGE plpgsql
AS $$
DECLARE
    v_resource_id int4;
BEGIN
    SELECT id INTO v_resource_id
    FROM pm.resource
    WHERE project_id = p_project_id
      AND external_id = p_external_id
      AND deleted_at IS NULL
      AND (p_import_batch_id IS NULL OR import_batch_id = p_import_batch_id)
    ORDER BY import_batch_id DESC
    LIMIT 1;
    
    RETURN v_resource_id;
END;
$$;

-- Função helper para buscar calendar_id por external_id
CREATE OR REPLACE FUNCTION pm.get_calendar_id_by_external_id(
    p_project_id int4,
    p_external_id varchar,
    p_import_batch_id int4 DEFAULT NULL
) RETURNS int4
LANGUAGE plpgsql
AS $$
DECLARE
    v_calendar_id int4;
BEGIN
    SELECT id INTO v_calendar_id
    FROM pm.calendar
    WHERE project_id = p_project_id
      AND external_id = p_external_id
      AND deleted_at IS NULL
      AND (p_import_batch_id IS NULL OR import_batch_id = p_import_batch_id)
    ORDER BY import_batch_id DESC
    LIMIT 1;
    
    RETURN v_calendar_id;
END;
$$;

-- Permissões para as funções
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pm TO alpha;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pm TO usage_on_tables;
