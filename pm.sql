-- DROP SCHEMA pm;
CREATE SCHEMA pm AUTHORIZATION alpha;

-- pm.project definition
-- Drop table
-- DROP TABLE pm.project;
CREATE TABLE pm.project (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    "name" varchar NOT NULL,
    external_id varchar NULL,
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
CREATE INDEX project_external_id_index ON pm.project USING btree (external_id);
CREATE INDEX project_start_date_index ON pm.project USING btree (start_date);
CREATE INDEX project_finish_date_index ON pm.project USING btree (finish_date);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.project FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.project OWNER TO alpha;
GRANT ALL ON TABLE pm.project TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.project TO usage_on_tables;

-- pm.import_log definition (auditoria de importações - arquivo fica no S3)
-- Drop table
-- DROP TABLE pm.import_log;
CREATE TABLE pm.import_log (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    source_file varchar NOT NULL,
    file_storage_path varchar NULL,
    file_hash varchar NULL,
    -- Contagens de entidades importadas
    custom_field_definitions int4 DEFAULT 0 NOT NULL,
    tasks int4 DEFAULT 0 NOT NULL,
    resources int4 DEFAULT 0 NOT NULL,
    assignments int4 DEFAULT 0 NOT NULL,
    calendars int4 DEFAULT 0 NOT NULL,
    dependencies int4 DEFAULT 0 NOT NULL,
    -- Timings (em milissegundos)
    total_time_ms numeric(12, 2) NULL,
    timings_ms jsonb NULL,
    -- Status e erro
    status varchar DEFAULT 'completed' NOT NULL,
    error_message text NULL,
    -- Stats adicionais (JSONB para flexibilidade)
    stats jsonb NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    CONSTRAINT import_log_pk PRIMARY KEY (id),
    CONSTRAINT import_log_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX import_log_project_id_index ON pm.import_log USING btree (project_id);
CREATE INDEX import_log_created_at_index ON pm.import_log USING btree (created_at);
CREATE INDEX import_log_status_index ON pm.import_log USING btree (status);
-- Permissions
ALTER TABLE pm.import_log OWNER TO alpha;
GRANT ALL ON TABLE pm.import_log TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.import_log TO usage_on_tables;

-- pm.task definition
-- Drop table
-- DROP TABLE pm.task;
CREATE TABLE pm.task (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
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
    custom_fields jsonb DEFAULT '{}' NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT task_pk PRIMARY KEY (id),
    CONSTRAINT task_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX task_project_id_index ON pm.task USING btree (project_id);
CREATE INDEX task_external_id_index ON pm.task USING btree (external_id);
CREATE INDEX task_start_date_index ON pm.task USING btree (start_date);
CREATE INDEX task_finish_date_index ON pm.task USING btree (finish_date);
CREATE INDEX task_wbs_index ON pm.task USING btree (wbs);
CREATE UNIQUE INDEX task_unique_active ON pm.task USING btree (project_id, external_id)
WHERE (deleted_at IS NULL AND external_id IS NOT NULL);
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
    external_id varchar NULL,
    "name" varchar NOT NULL,
    email varchar NULL,
    "type" varchar NULL,
    "group" varchar NULL,
    max_units numeric(10, 2) NULL,
    standard_rate numeric(15, 2) NULL,
    cost numeric(15, 2) NULL,
    notes text NULL,
    custom_fields jsonb DEFAULT '{}' NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT resource_pk PRIMARY KEY (id),
    CONSTRAINT resource_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX resource_project_id_index ON pm.resource USING btree (project_id);
CREATE INDEX resource_external_id_index ON pm.resource USING btree (external_id);
CREATE INDEX resource_name_index ON pm.resource USING btree (name);
CREATE INDEX resource_email_index ON pm.resource USING btree (email);
CREATE UNIQUE INDEX resource_unique_active ON pm.resource USING btree (project_id, external_id)
WHERE (deleted_at IS NULL AND external_id IS NOT NULL);
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
    external_id varchar NULL,
    task_id int4 NOT NULL,
    resource_id int4 NOT NULL,
    work numeric(10, 2) NULL,
    cost numeric(15, 2) NULL,
    start_date timestamp NULL,
    finish_date timestamp NULL,
    units numeric(10, 2) NULL,
    percent_complete int4 DEFAULT 0 NOT NULL,
    custom_fields jsonb DEFAULT '{}' NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT assignment_pk PRIMARY KEY (id),
    CONSTRAINT assignment_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id),
    CONSTRAINT assignment_task_id_fk FOREIGN KEY (task_id) REFERENCES pm.task(id),
    CONSTRAINT assignment_resource_id_fk FOREIGN KEY (resource_id) REFERENCES pm.resource(id)
);
CREATE INDEX assignment_project_id_index ON pm.assignment USING btree (project_id);
CREATE INDEX assignment_external_id_index ON pm.assignment USING btree (external_id);
CREATE INDEX assignment_task_id_index ON pm.assignment USING btree (task_id);
CREATE INDEX assignment_resource_id_index ON pm.assignment USING btree (resource_id);
CREATE UNIQUE INDEX assignment_unique_active ON pm.assignment USING btree (project_id, external_id)
WHERE (deleted_at IS NULL AND external_id IS NOT NULL);
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
    CONSTRAINT task_dependency_predecessor_task_id_fk FOREIGN KEY (predecessor_task_id) REFERENCES pm.task(id),
    CONSTRAINT task_dependency_successor_task_id_fk FOREIGN KEY (successor_task_id) REFERENCES pm.task(id)
);
CREATE INDEX task_dependency_project_id_index ON pm.task_dependency USING btree (project_id);
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
    CONSTRAINT calendar_parent_calendar_id_fk FOREIGN KEY (parent_calendar_id) REFERENCES pm.calendar(id)
);
CREATE INDEX calendar_project_id_index ON pm.calendar USING btree (project_id);
CREATE INDEX calendar_external_id_index ON pm.calendar USING btree (external_id);
CREATE INDEX calendar_parent_calendar_id_index ON pm.calendar USING btree (parent_calendar_id);
CREATE UNIQUE INDEX calendar_unique_active ON pm.calendar USING btree (project_id, external_id)
WHERE (deleted_at IS NULL AND external_id IS NOT NULL);
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
    day_of_week int4 NOT NULL,
    working bool DEFAULT true NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT calendar_weekday_pk PRIMARY KEY (id),
    CONSTRAINT calendar_weekday_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id)
);
CREATE INDEX calendar_weekday_calendar_id_index ON pm.calendar_weekday USING btree (calendar_id);
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
    CONSTRAINT calendar_working_time_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id)
);
CREATE INDEX calendar_working_time_calendar_id_index ON pm.calendar_working_time USING btree (calendar_id);
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
    CONSTRAINT calendar_exception_calendar_id_fk FOREIGN KEY (calendar_id) REFERENCES pm.calendar(id)
);
CREATE INDEX calendar_exception_calendar_id_index ON pm.calendar_exception USING btree (calendar_id);
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
    CONSTRAINT assignment_timephased_planned_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES pm.assignment(id)
);
CREATE INDEX assignment_timephased_planned_assignment_id_index ON pm.assignment_timephased_planned USING btree (assignment_id);
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
    CONSTRAINT assignment_timephased_complete_assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES pm.assignment(id)
);
CREATE INDEX assignment_timephased_complete_assignment_id_index ON pm.assignment_timephased_complete USING btree (assignment_id);
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
    external_id varchar NULL,
    "name" varchar NOT NULL,
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT baseline_pk PRIMARY KEY (id),
    CONSTRAINT baseline_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX baseline_project_id_index ON pm.baseline USING btree (project_id);
CREATE INDEX baseline_external_id_index ON pm.baseline USING btree (external_id);
CREATE INDEX baseline_name_index ON pm.baseline USING btree (name);
CREATE UNIQUE INDEX baseline_unique_active ON pm.baseline USING btree (project_id, external_id)
WHERE (deleted_at IS NULL AND external_id IS NOT NULL);
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
    CONSTRAINT task_baseline_task_id_fk FOREIGN KEY (task_id) REFERENCES pm.task(id)
);
CREATE INDEX task_baseline_baseline_id_index ON pm.task_baseline USING btree (baseline_id);
CREATE INDEX task_baseline_task_id_index ON pm.task_baseline USING btree (task_id);
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
    CONSTRAINT resource_baseline_resource_id_fk FOREIGN KEY (resource_id) REFERENCES pm.resource(id)
);
CREATE INDEX resource_baseline_baseline_id_index ON pm.resource_baseline USING btree (baseline_id);
CREATE INDEX resource_baseline_resource_id_index ON pm.resource_baseline USING btree (resource_id);
CREATE UNIQUE INDEX resource_baseline_unique_active ON pm.resource_baseline USING btree (baseline_id, resource_id)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.resource_baseline FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.resource_baseline OWNER TO alpha;
GRANT ALL ON TABLE pm.resource_baseline TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.resource_baseline TO usage_on_tables;

-- pm.custom_field_definition definition (metadados dos campos customizados)
-- Drop table
-- DROP TABLE pm.custom_field_definition;
CREATE TABLE pm.custom_field_definition (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    project_id int4 NOT NULL,
    field_type varchar NOT NULL,
    field_class varchar NOT NULL,
    alias varchar NULL,
    data_type varchar NOT NULL DEFAULT 'STRING',
    created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by int4 NOT NULL,
    updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_by int4 NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT custom_field_definition_pk PRIMARY KEY (id),
    CONSTRAINT custom_field_definition_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX custom_field_definition_project_id_index ON pm.custom_field_definition USING btree (project_id);
CREATE INDEX custom_field_definition_field_type_index ON pm.custom_field_definition USING btree (field_type);
CREATE INDEX custom_field_definition_field_class_index ON pm.custom_field_definition USING btree (field_class);
CREATE UNIQUE INDEX custom_field_definition_unique_active ON pm.custom_field_definition USING btree (project_id, field_type, field_class)
WHERE (deleted_at IS NULL);
-- Table Triggers
CREATE TRIGGER trigger_set_updated_at BEFORE UPDATE ON pm.custom_field_definition FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- Permissions
ALTER TABLE pm.custom_field_definition OWNER TO alpha;
GRANT ALL ON TABLE pm.custom_field_definition TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.custom_field_definition TO usage_on_tables;

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

-- pm.virtual_site_project definition
-- Drop table
-- DROP TABLE pm.virtual_site_project;
CREATE TABLE pm.virtual_site_project (
    id int4 GENERATED ALWAYS AS IDENTITY(
        INCREMENT BY 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1 NO CYCLE
    ) NOT NULL,
    virtual_site_id int4 NOT NULL,
    project_id int4 NOT NULL,
    created_at timestamp DEFAULT now() NOT NULL,
    created_by int4 NOT NULL,
    deleted_at timestamp NULL,
    deleted_by int4 NULL,
    CONSTRAINT virtual_site_project_pk PRIMARY KEY (id),
    CONSTRAINT virtual_site_project_project_id_fk FOREIGN KEY (project_id) REFERENCES pm.project(id)
);
CREATE INDEX virtual_site_project_project_id_index ON pm.virtual_site_project USING btree (project_id);
CREATE INDEX virtual_site_project_virtual_site_id_index ON pm.virtual_site_project USING btree (virtual_site_id);
CREATE UNIQUE INDEX virtual_site_project_unique_active ON pm.virtual_site_project USING btree (project_id, virtual_site_id)
WHERE (deleted_at IS NULL);
-- Permissions
ALTER TABLE pm.virtual_site_project OWNER TO alpha;
GRANT ALL ON TABLE pm.virtual_site_project TO alpha;
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLE pm.virtual_site_project TO usage_on_tables;

-- Permissions
GRANT ALL ON SCHEMA pm TO alpha;
GRANT USAGE ON SCHEMA pm TO usage_on_tables;
ALTER DEFAULT PRIVILEGES FOR ROLE alpha IN SCHEMA pm
GRANT SELECT, DELETE, INSERT, UPDATE ON TABLES TO usage_on_tables;
