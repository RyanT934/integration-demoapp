CREATE TABLE app_logs (
    id SERIAL PRIMARY KEY,
    run_date TIMESTAMP NOT NULL,
    message TEXT NOT NULL
);
