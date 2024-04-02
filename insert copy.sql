DO
$$
DECLARE
    table_name TEXT;
BEGIN
    FOR table_name IN
        SELECT tablename
        FROM pg_catalog.pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS public."' || table_name || '" CASCADE;';
    END LOOP;
END
$$;




-- Create Animal table
CREATE TABLE IF NOT EXISTS "Animal" (
    id SERIAL PRIMARY KEY,
    genus VARCHAR(120) NOT NULL,
    specificepithet VARCHAR(120) NOT NULL
    );





-- Create Institution table
CREATE TABLE IF NOT EXISTS "Institution" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    street VARCHAR(120) NOT NULL
    );

CREATE TABLE IF NOT EXISTS "Specimen" (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER REFERENCES "Animal"(id) NOT NULL,
    institution_id INTEGER REFERENCES "Institution"(id) NOT NULL,
    sightingdate TIMESTAMP NOT NULL
    );


-- Insert data into Animal table
INSERT INTO "Animal" (genus, specificepithet) VALUES
    ('Canis', 'lupus'),
    ('Canis', 'familiaris'),
    ('Felis', 'catus'),
    ('Felis', 'lynx'),
    ('Panthera', 'leo'),
    ('Panthera', 'tigris'),
    ('Ursus', 'arctos'),
    ('Equus', 'ferus'),
    ('Bos', 'taurus'),
    ('Gallus', 'domesticus');


-- Insert data into Institution table
INSERT INTO "Institution" (name, street) VALUES
    ('Zoo A', '123 Main St'),
    ('Wildlife Sanctuary B', '456 Oak Ave'),
    ('Research Institute C', '789 Elm Blvd'),
    ('Animal Rescue Center D', '101 Pine St'),
    ('Nature Park E', '202 Maple Ave'),
    ('Conservation Society F', '303 Cedar St'),
    ('Aquarium G', '404 Birch Ave'),
    ('Veterinary Hospital H', '505 Walnut St'),
    ('Aviary I', '606 Spruce Ave'),
    ('Museum of Natural History J', '707 Pinecone Blvd');



INSERT INTO "Specimen" (animal_id, institution_id, sightingdate) VALUES
    (1, 1, '2023-01-15 10:30:00'),
    (2, 2, '2023-02-20 14:45:00'),
    (3, 3, '2023-03-10 09:00:00');

