
INSERT INTO  carlos.device(device_id, display_name, description, registered_at, last_seen_at)
VALUES
    ('1c25f25f-0207-41eb-8ab4-d9fe069031ff', 'Device (Online)', 'This device is online.', '2024-04-14 18:16:15 +02:00', NOW() AT TIME ZONE 'UTC'),
    ('fe86328a-8d19-47f4-b1c0-d88f6a89e5a4', 'Device (Offline)', 'Used to test devices that are marked as offline.', '2024-04-14 18:16:15 +02:00', '2024-04-14 18:17:15 +02:00'),
    ('0874ecc9-1169-4fb0-80d2-e5b0d08754e4', 'Device (Offline)', 'Used to test devices that have never been connected.', '2024-04-14 18:16:15 +02:00', null);
