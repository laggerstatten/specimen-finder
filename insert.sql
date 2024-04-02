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
    sciname VARCHAR(255),
    maincommonname VARCHAR(255),
    taxonorder VARCHAR(255),
    genus VARCHAR(255),
    specificepithet VARCHAR(255),
    biogeographicrealm VARCHAR(255),
    iucnstatus VARCHAR(255)
    );





-- Create Institution table
CREATE TABLE IF NOT EXISTS "Institution" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    street VARCHAR(255) NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL
    );

CREATE TABLE IF NOT EXISTS "Specimen" (
    id SERIAL PRIMARY KEY,
    animal_id INTEGER REFERENCES "Animal"(id) NOT NULL,
    institution_id INTEGER REFERENCES "Institution"(id) NOT NULL,
    sightingdate TIMESTAMP NOT NULL
    );


-- Insert data into Animal table
INSERT INTO "Animal" (sciname, maincommonname, taxonorder, genus, specificepithet, biogeographicrealm, iucnstatus) VALUES
    ('Didelphis_virginiana', 'Virginia Opossum', 'DIDELPHIMORPHIA', 'Didelphis', 'virginiana', 'Nearctic|Neotropic', 'LC'),
    ('Osphranter_rufus', 'Red Kangaroo', 'DIPROTODONTIA', 'Osphranter', 'rufus', 'Australasia/Oceania', 'LC'),
    ('Phascolarctos_cinereus', 'Koala', 'DIPROTODONTIA', 'Phascolarctos', 'cinereus', 'Australasia/Oceania', 'VU'),
    ('Chlamyphorus_truncatus', 'Pink Fairy Armadillo', 'CINGULATA', 'Chlamyphorus', 'truncatus', 'Neotropic', 'DD'),
    ('Choloepus_didactylus', 'Linnaeus''s Two-toed Sloth', 'PILOSA', 'Choloepus', 'didactylus', 'Neotropic', 'LC'),
    ('Myrmecophaga_tridactyla', 'Giant Anteater', 'PILOSA', 'Myrmecophaga', 'tridactyla', 'Neotropic', 'VU'),
    ('Elephas_maximus', 'Asian Elephant', 'PROBOSCIDEA', 'Elephas', 'maximus', 'Indomalaya', 'EN'),
    ('Pan_troglodytes', 'Chimpanzee', 'PRIMATES', 'Pan', 'troglodytes', 'Afrotropic', 'EN'),
    ('Leontopithecus_chrysomelas', 'Golden-headed Lion Tamarin', 'PRIMATES', 'Leontopithecus', 'chrysomelas', 'Neotropic', 'EN'),
    ('Varecia_variegata', 'Black-and-white Ruffed Lemur', 'PRIMATES', 'Varecia', 'variegata', 'Afrotropic', 'CR'),
    ('Lepus_townsendii', 'White-tailed Jackrabbit', 'LAGOMORPHA', 'Lepus', 'townsendii', 'Nearctic', 'LC'),
    ('Hydrochoerus_hydrochaeris', 'Greater Capybara', 'RODENTIA', 'Hydrochoerus', 'hydrochaeris', 'Neotropic', 'LC'),
    ('Erethizon_dorsatum', 'North American Porcupine', 'RODENTIA', 'Erethizon', 'dorsatum', 'Nearctic', 'LC'),
    ('Heterocephalus_glaber', 'Naked Mole-rat', 'RODENTIA', 'Heterocephalus', 'glaber', 'Afrotropic', 'LC'),
    ('Cynomys_mexicanus', 'Mexican Prairie Dog', 'RODENTIA', 'Cynomys', 'mexicanus', 'Nearctic', 'EN'),
    ('Castor_canadensis', 'North American Beaver', 'RODENTIA', 'Castor', 'canadensis', 'Nearctic', 'LC'),
    ('Gulo_gulo', 'Wolverine', 'CARNIVORA', 'Gulo', 'gulo', 'Nearctic|Palearctic', 'LC'),
    ('Mellivora_capensis', 'Honey Badger', 'CARNIVORA', 'Mellivora', 'capensis', 'Afrotropic|Indomalaya', 'LC'),
    ('Zalophus_californianus', 'California Sea Lion', 'CARNIVORA', 'Zalophus', 'californianus', 'Marine', 'LC'),
    ('Ursus_maritimus', 'Polar Bear', 'CARNIVORA', 'Ursus', 'maritimus', 'Nearctic|Palearctic', 'VU'),
    ('Vulpes_lagopus', 'Arctic Fox', 'CARNIVORA', 'Vulpes', 'lagopus', 'Nearctic|Palearctic', 'LC'),
    ('Acinonyx_jubatus', 'Cheetah', 'CARNIVORA', 'Acinonyx', 'jubatus', 'Afrotropic|Indomalaya|Palearctic', 'VU'),
    ('Leopardus_pardalis', 'Ocelot', 'CARNIVORA', 'Leopardus', 'pardalis', 'Neotropic', 'LC'),
    ('Ceratotherium_simum', 'White Rhinoceros', 'PERISSODACTYLA', 'Ceratotherium', 'simum', 'Afrotropic', 'NT'),
    ('Tapirus_pinchaque', '	Mountain Tapir', 'PERISSODACTYLA', 'Tapirus', 'pinchaque', 'Neotropic', 'EN'),
    ('Equus_quagga', 'Plains Zebra', 'PERISSODACTYLA', 'Equus', 'quagga', 'Afrotropic', 'NT'),
    ('Ovis_canadensis', 'Bighorn Sheep', 'ARTIODACTYLA', 'Ovis', 'canadensis', 'Nearctic', 'LC'),
    ('Alces_alces', 'Moose', 'ARTIODACTYLA', 'Alces', 'alces', 'Nearctic|Palearctic', 'LC'),
    ('Giraffa_reticulata', 'Reticulated Giraffe', 'ARTIODACTYLA', 'Giraffa', 'reticulata', 'Afrotropic', 'NA'),
    ('Lama_glama', 'Llama', 'ARTIODACTYLA', 'Lama', 'glama', 'Domesticated', 'NA'),
    ('Hippopotamus_amphibius', 'Common Hippopotamus', 'ARTIODACTYLA', 'Hippopotamus', 'amphibius', 'Afrotropic', 'VU');


-- Insert data into Institution table
INSERT INTO "Institution" (name, street, longitude, latitude, city, state) VALUES
    ('Little Rock Zoo', '1 Zoo Dr', -92.351204, 34.750324, 'Little Rock', 'AR'),
    ('Phoenix Zoo', '455 N Galvin Pkwy', -111.954294, 33.453572, 'Phoenix', 'AZ'),
    ('Arizona-Sonora Desert Museum', '2021 N Kinney Rd', -111.162939, 32.243347, 'Tucson', 'AZ'),
    ('Birch Aquarium at Scripps Institution of Oceanography', '2300 Expedition Way', -117.250643, 32.865776, 'La Jolla', 'CA'),
    ('Aquarium of the Pacific', '100 Aquarium Way', -118.196697, 33.763321, 'Long Beach', 'CA'),
    ('Monterey Bay Aquarium', '886 Cannery Row', -121.901874, 36.61783, 'Monterey', 'CA'),
    ('San Diego Zoo', '2920 Zoo Dr', -117.148743, 32.737832, 'San Diego', 'CA'),
    ('Cheyenne Mountain Zoo', '4250 Cheyenne Mountain Zoo Rd', -104.851862, 38.771427, 'Colorado Springs', 'CO'),
    ('Georgia Aquarium', '225 Baker St Nw', -84.394046, 33.762291, 'Atlanta', 'GA'),
    ('John G. Shedd Aquarium', '1200 S. DuSable Lake Shore Dr', -87.614038, 41.8675726, 'Chicago', 'IL'),
    ('Sedgwick County Zoo', '5555 W Zoo Blvd', -97.40957, 37.722652, 'Wichita', 'KS'),
    ('Lincoln Children''s Zoo', '1222 S 27th ST', -96.697998, 40.785809, 'Lincoln', 'NE'),
    ('Omaha''s Henry Doorly Zoo & Aquarium', '3701 S 10Th St', -95.929451, 41.224716, 'Omaha', 'NE'),
    ('Albuquerque Biological Park', '903 10Th St Sw', -106.659721, 35.075626, 'Albuquerque', 'NM'),
    ('Bronx Zoo', '2300 Southern Blvd', -73.881668, 40.853348, 'Bronx', 'NY'),
    ('Columbus Zoo and Aquarium', '4850 Powell Rd', -83.094185, 40.17754, 'Powell', 'OH'),
    ('Oklahoma City Zoo and Botanical Garden', '2000 Remington Pl', -97.458588, 35.705735, 'Oklahoma City', 'OK'),
    ('Tennessee Aquarium', '1 Broad St', -85.310844, 35.054745, 'Chattanooga', 'TN'),
    ('Texas State Aquarium', '2710 N Shoreline Blvd', -97.391981, 27.814687, 'Corpus Christi', 'TX'),
    ('Dallas Zoo', '650 S R L Thornton Fwy', -96.813034, 32.744675, 'Dallas', 'TX'),
    ('Fort Worth Zoo', '1989 Colonial Pkwy', -97.360077, 32.722649, 'Fort Worth', 'TX'),
    ('Houston Zoo, Inc.', '6200 Hermann Park Dr', -95.401749, 29.706787, 'Houston', 'TX'),
    ('San Antonio Zoological Society', '3903 N Saint Marys St', -98.473658, 29.462071, 'San Antonio', 'TX');



INSERT INTO "Specimen" (animal_id, institution_id, sightingdate) VALUES
    (1, 1, '2023-01-15 10:30:00'),
    (2, 2, '2023-02-20 14:45:00'),
    (3, 3, '2023-03-10 09:00:00');

