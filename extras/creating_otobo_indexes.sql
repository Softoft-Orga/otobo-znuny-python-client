-- ticket
CREATE INDEX IF NOT EXISTS ticket_queue_id               ON ticket(queue_id);
CREATE INDEX IF NOT EXISTS ticket_state_id               ON ticket(ticket_state_id);
CREATE INDEX IF NOT EXISTS ticket_user_id                ON ticket(user_id);
CREATE INDEX IF NOT EXISTS ticket_resp_user_id           ON ticket(responsible_user_id);
CREATE INDEX IF NOT EXISTS ticket_customer_id            ON ticket(customer_id);
CREATE INDEX IF NOT EXISTS ticket_customer_user_id       ON ticket(customer_user_id);
CREATE INDEX IF NOT EXISTS ticket_service_id             ON ticket(service_id);
CREATE INDEX IF NOT EXISTS ticket_sla_id                 ON ticket(sla_id);
CREATE INDEX IF NOT EXISTS ticket_create_time            ON ticket(create_time);
CREATE INDEX IF NOT EXISTS ticket_change_time            ON ticket(change_time);
CREATE INDEX IF NOT EXISTS ticket_until_time             ON ticket(until_time);
CREATE INDEX IF NOT EXISTS ticket_escalation_time        ON ticket(escalation_time);
CREATE INDEX IF NOT EXISTS ticket_escalation_update      ON ticket(escalation_update_time);
CREATE INDEX IF NOT EXISTS ticket_escalation_response    ON ticket(escalation_response_time);
CREATE INDEX IF NOT EXISTS ticket_escalation_solution    ON ticket(escalation_solution_time);
CREATE INDEX IF NOT EXISTS ticket_archive_flag           ON ticket(archive_flag);

-- ticket_history (für Change/Close-Filter)
CREATE INDEX IF NOT EXISTS th_ticket_time                ON ticket_history(ticket_id, create_time);
CREATE INDEX IF NOT EXISTS th_type_state_time            ON ticket_history(history_type_id, state_id, create_time);
CREATE INDEX IF NOT EXISTS th_ticket_type_state_time     ON ticket_history(ticket_id, history_type_id, state_id, create_time);

-- article
CREATE INDEX IF NOT EXISTS art_ticket_id                 ON article(ticket_id);
CREATE INDEX IF NOT EXISTS art_visible_time              ON article(is_visible_for_customer, create_time);

-- dynamic_field_value
CREATE INDEX IF NOT EXISTS dfv_field_object              ON dynamic_field_value(field_id, object_id);
CREATE INDEX IF NOT EXISTS dfv_object_field              ON dynamic_field_value(object_id, field_id);
CREATE INDEX IF NOT EXISTS dfv_field_value_int           ON dynamic_field_value(field_id, value_int);
CREATE INDEX IF NOT EXISTS dfv_field_value_text          ON dynamic_field_value(field_id, value_text(191));
CREATE INDEX IF NOT EXISTS dfv_field_value_date          ON dynamic_field_value(field_id, value_date);
