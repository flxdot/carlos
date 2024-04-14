
INSERT INTO  carlos.device(device_id, display_name, description, registered_at, last_seen_at)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Device (Online)', 'This device is online.', '2024-04-14 18:16:15 +02:00', NOW() AT TIME ZONE 'UTC'),
    ('22222222-2222-2222-2222-222222222222', 'Device (Offline)', 'Used to test devices that are marked as offline.', '2024-04-14 18:16:15 +02:00', '2024-04-14 18:17:15 +02:00'),
    ('33333333-3333-3333-3333-333333333333', 'Device (Disconnected)', 'Used to test devices that have never been connected.', '2024-04-14 18:16:15 +02:00', null),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Device A', 'Used to test interaction with a device.', '2024-04-14 18:16:15 +02:00', null);
