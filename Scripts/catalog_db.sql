PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS regions (
    id INTEGER PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS comunas (
    id INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    region_id INTEGER NOT NULL,
    FOREIGN KEY(region_id) REFERENCES regions(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    nombre TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    id INTEGER PRIMARY KEY,
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    direccion TEXT,
    region_id INTEGER NOT NULL,
    comuna_id INTEGER NOT NULL,
    FOREIGN KEY(region_id) REFERENCES regions(id),
    FOREIGN KEY(comuna_id) REFERENCES comunas(id)
);

CREATE TABLE IF NOT EXISTS products (
    sku TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    precio_lista INTEGER NOT NULL,
    descuento_efectivo REAL NOT NULL DEFAULT 0,
    category_id INTEGER NOT NULL,
    FOREIGN KEY(category_id) REFERENCES categories(id)
);

CREATE TABLE IF NOT EXISTS inventory (
    branch_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    cantidad INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY(branch_id, sku),
    FOREIGN KEY(branch_id) REFERENCES branches(id),
    FOREIGN KEY(sku) REFERENCES products(sku)
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    branch_id INTEGER NOT NULL,
    cliente_nombre TEXT,
    total INTEGER NOT NULL,
    FOREIGN KEY(branch_id) REFERENCES branches(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio_unitario INTEGER NOT NULL,
    descuento REAL NOT NULL DEFAULT 0,
    PRIMARY KEY(order_id, sku),
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(sku) REFERENCES products(sku)
);

INSERT INTO regions (id, nombre) VALUES (1, 'Metropolitana');
INSERT INTO regions (id, nombre) VALUES (2, 'Valparaíso');
INSERT INTO regions (id, nombre) VALUES (3, 'Biobío');

INSERT INTO comunas (id, nombre, region_id) VALUES (1, 'Santiago', 1);
INSERT INTO comunas (id, nombre, region_id) VALUES (2, 'Providencia', 1);
INSERT INTO comunas (id, nombre, region_id) VALUES (3, 'Viña del Mar', 2);
INSERT INTO comunas (id, nombre, region_id) VALUES (4, 'Valparaíso', 2);
INSERT INTO comunas (id, nombre, region_id) VALUES (5, 'Concepción', 3);

INSERT INTO categories (id, nombre) VALUES (1, 'procesadores');
INSERT INTO categories (id, nombre) VALUES (2, 'video');
INSERT INTO categories (id, nombre) VALUES (3, 'ram');
INSERT INTO categories (id, nombre) VALUES (4, 'almacenamiento');
INSERT INTO categories (id, nombre) VALUES (5, 'placas');
INSERT INTO categories (id, nombre) VALUES (6, 'accesorios');
INSERT INTO categories (id, nombre) VALUES (7, 'monitores');
INSERT INTO categories (id, nombre) VALUES (8, 'perifericos');
INSERT INTO categories (id, nombre) VALUES (9, 'fuentes');
INSERT INTO categories (id, nombre) VALUES (10, 'gabinetes');
INSERT INTO categories (id, nombre) VALUES (11, 'refrigeracion');

INSERT INTO branches (id, codigo, nombre, direccion, region_id, comuna_id) VALUES (1, 'SCL-CENTRO', 'PC Factory Santiago Centro', 'Av. Libertador Bernardo O''Higgins 100', 1, 1);
INSERT INTO branches (id, codigo, nombre, direccion, region_id, comuna_id) VALUES (2, 'SCL-PROVIDENCIA', 'PC Factory Providencia', 'Av. Providencia 2050', 1, 2);
INSERT INTO branches (id, codigo, nombre, direccion, region_id, comuna_id) VALUES (3, 'VLA-VINA', 'PC Factory Viña del Mar', 'Av. Libertad 430', 2, 3);
INSERT INTO branches (id, codigo, nombre, direccion, region_id, comuna_id) VALUES (4, 'VLA-VALPO', 'PC Factory Valparaíso', 'Av. España 1650', 2, 4);
INSERT INTO branches (id, codigo, nombre, direccion, region_id, comuna_id) VALUES (5, 'BIO-CONCE', 'PC Factory Concepción', 'Calle Chacabuco 700', 3, 5);

INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-AMD-R5-5600X', 'Procesador AMD Ryzen 5 5600X (6 Núcleos / 12 Hilos)', 'Procesador AMD Ryzen 5 5600X (6 Núcleos / 12 Hilos)', 169990, 0.08, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-AMD-R7-5700X', 'Procesador AMD Ryzen 7 5700X (8 Núcleos / 16 Hilos)', 'Procesador AMD Ryzen 7 5700X (8 Núcleos / 16 Hilos)', 219990, 0.10, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-AMD-R7-7800X3D', 'Procesador AMD Ryzen 7 7800X3D (El rey del Gaming)', 'Procesador AMD Ryzen 7 7800X3D (El rey del Gaming)', 449990, 0.05, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-INTEL-I3-12100F', 'Procesador Intel Core i3-12100F (4 Núcleos / 8 Hilos)', 'Procesador Intel Core i3-12100F (4 Núcleos / 8 Hilos)', 89990, 0.00, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-INTEL-I5-12400F', 'Procesador Intel Core i5-12400F (6 Núcleos / 12 Hilos)', 'Procesador Intel Core i5-12400F (6 Núcleos / 12 Hilos)', 145990, 0.07, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-INTEL-I5-14600K', 'Procesador Intel Core i5-14600K (14 Núcleos / 20 Hilos)', 'Procesador Intel Core i5-14600K (14 Núcleos / 20 Hilos)', 359990, 0.05, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CPU-INTEL-I7-14700K', 'Procesador Intel Core i7-14700K (20 Núcleos / 28 Hilos)', 'Procesador Intel Core i7-14700K (20 Núcleos / 28 Hilos)', 489990, 0.10, 1);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-NVIDIA-RTX3050', 'Tarjeta de Video NVIDIA GeForce RTX 3050 8GB GDDR6', 'Tarjeta de Video NVIDIA GeForce RTX 3050 8GB GDDR6', 249990, 0.05, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-NVIDIA-RTX4060', 'Tarjeta de Video NVIDIA GeForce RTX 4060 8GB GDDR6', 'Tarjeta de Video NVIDIA GeForce RTX 4060 8GB GDDR6', 369990, 0.08, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-NVIDIA-RTX4070-SUPER', 'Tarjeta de Video NVIDIA GeForce RTX 4070 Super 12GB GDDR6X', 'Tarjeta de Video NVIDIA GeForce RTX 4070 Super 12GB GDDR6X', 699990, 0.12, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-NVIDIA-RTX4080-SUPER', 'Tarjeta de Video NVIDIA GeForce RTX 4080 Super 16GB GDDR6X', 'Tarjeta de Video NVIDIA GeForce RTX 4080 Super 16GB GDDR6X', 1249990, 0.10, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-AMD-RX6600', 'Tarjeta de Video AMD Radeon RX 6600 8GB GDDR6', 'Tarjeta de Video AMD Radeon RX 6600 8GB GDDR6', 239990, 0.00, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-AMD-RX7600XT', 'Tarjeta de Video AMD Radeon RX 7600 XT 16GB GDDR6', 'Tarjeta de Video AMD Radeon RX 7600 XT 16GB GDDR6', 399990, 0.05, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('GPU-AMD-RX7800XT', 'Tarjeta de Video AMD Radeon RX 7800 XT 16GB GDDR6', 'Tarjeta de Video AMD Radeon RX 7800 XT 16GB GDDR6', 589990, 0.07, 2);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-KINGSTON-8GB-DDR4', 'Memoria RAM Kingston Fury Beast 8GB DDR4 3200MHz', 'Memoria RAM Kingston Fury Beast 8GB DDR4 3200MHz', 24990, 0.00, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-KINGSTON-16GB-DDR4', 'Memoria RAM Kingston Fury Beast 16GB DDR4 3200MHz', 'Memoria RAM Kingston Fury Beast 16GB DDR4 3200MHz', 44990, 0.05, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-CORSAIR-16GB-DDR4', 'Memoria RAM Corsair Vengeance LPX 16GB (2x8GB) DDR4 3600MHz', 'Memoria RAM Corsair Vengeance LPX 16GB (2x8GB) DDR4 3600MHz', 52990, 0.08, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-CRUCIAL-16GB-DDR5', 'Memoria RAM Crucial Classic 16GB DDR5 4800MHz', 'Memoria RAM Crucial Classic 16GB DDR5 4800MHz', 59990, 0.00, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-CORSAIR-32GB-DDR5', 'Memoria RAM Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz', 'Memoria RAM Corsair Vengeance RGB 32GB (2x16GB) DDR5 6000MHz', 129990, 0.10, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('RAM-G_SKILL-32GB-DDR5', 'Memoria RAM G.Skill Trident Z5 Neo 32GB (2x16GB) DDR5 6000MHz', 'Memoria RAM G.Skill Trident Z5 Neo 32GB (2x16GB) DDR5 6000MHz', 139990, 0.05, 3);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('SSD-KINGSTON-500GB', 'Unidad SSD Kingston NV2 500GB NVMe PCIe 4.0 M.2', 'Unidad SSD Kingston NV2 500GB NVMe PCIe 4.0 M.2', 39990, 0.00, 4);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('SSD-CRUCIAL-1TB', 'Unidad SSD Crucial P3 Plus 1TB NVMe PCIe 4.0 M.2', 'Unidad SSD Crucial P3 Plus 1TB NVMe PCIe 4.0 M.2', 69990, 0.05, 4);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('SSD-SAMSUNG-1TB-990', 'Unidad SSD Samsung 990 PRO 1TB NVMe PCIe 4.0 M.2', 'Unidad SSD Samsung 990 PRO 1TB NVMe PCIe 4.0 M.2', 119990, 0.08, 4);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('SSD-SAMSUNG-2TB-990', 'Unidad SSD Samsung 990 PRO 2TB NVMe PCIe 4.0 M.2', 'Unidad SSD Samsung 990 PRO 2TB NVMe PCIe 4.0 M.2', 199990, 0.10, 4);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('HDD-SEAGATE-2TB', 'Disco Duro Interno Seagate BarraCuda 2TB 3.5" SATA3', 'Disco Duro Interno Seagate BarraCuda 2TB 3.5" SATA3', 59990, 0.00, 4);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MB-ASUS-H610M', 'Placa Madre ASUS Prime H610M-E D4 (Intel LGA1700)', 'Placa Madre ASUS Prime H610M-E D4 (Intel LGA1700)', 84990, 0.05, 5);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MB-MSI-B550M', 'Placa Madre MSI B550M PRO-VDH WIFI (AMD AM4)', 'Placa Madre MSI B550M PRO-VDH WIFI (AMD AM4)', 119990, 0.07, 5);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MB-ASUS-B760M', 'Placa Madre ASUS TUF Gaming B760M-PLUS WIFI (Intel LGA1700)', 'Placa Madre ASUS TUF Gaming B760M-PLUS WIFI (Intel LGA1700)', 169990, 0.08, 5);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MB-GIGABYTE-B650', 'Placa Madre Gigabyte B650 GAMING X AX (AMD AM5 DDR5)', 'Placa Madre Gigabyte B650 GAMING X AX (AMD AM5 DDR5)', 199990, 0.10, 5);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MB-ASUS-X670E', 'Placa Madre ASUS ROG Strix X670E-F Gaming WIFI (AMD AM5)', 'Placa Madre ASUS ROG Strix X670E-F Gaming WIFI (AMD AM5)', 399990, 0.12, 5);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('PSU-MSI-550W', 'Fuente de Poder MSI MAG A550BN 550W 80 PLUS Bronze', 'Fuente de Poder MSI MAG A550BN 550W 80 PLUS Bronze', 49990, 0.00, 9);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('PSU-EVGA-600W', 'Fuente de Poder EVGA 600W W1 80 Plus White', 'Fuente de Poder EVGA 600W W1 80 Plus White', 54990, 0.05, 9);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('PSU-CORSAIR-650W', 'Fuente de Poder Corsair CX650 M 650W 80 Plus Bronze Semi-Modular', 'Fuente de Poder Corsair CX650 M 650W 80 Plus Bronze Semi-Modular', 69990, 0.05, 9);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('PSU-GIGABYTE-750W', 'Fuente de Poder Gigabyte UD750GM 750W 80 Plus Gold Full Modular', 'Fuente de Poder Gigabyte UD750GM 750W 80 Plus Gold Full Modular', 94990, 0.08, 9);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('PSU-CORSAIR-850W', 'Fuente de Poder Corsair RM850e 850W 80 Plus Gold Full Modular ATX 3.0', 'Fuente de Poder Corsair RM850e 850W 80 Plus Gold Full Modular ATX 3.0', 129990, 0.10, 9);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CASE-MSI-FORGE', 'Gabinete MSI MAG Forge 112R (Vidrio Templado / 4 Ventiladores ARGB)', 'Gabinete MSI MAG Forge 112R (Vidrio Templado / 4 Ventiladores ARGB)', 59990, 0.05, 10);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CASE-COUGAR-ARCHON', 'Gabinete Cougar Archon 2 Mesh RGB Black', 'Gabinete Cougar Archon 2 Mesh RGB Black', 48990, 0.00, 10);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CASE-LIAN_LI-O11', 'Gabinete Lian Li O11 Dynamic EVO Black (Gama Premium)', 'Gabinete Lian Li O11 Dynamic EVO Black (Gama Premium)', 169990, 0.10, 10);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('COOLER-DEEPCOOL-AG400', 'Refrigeración por Aire Deepcool AG400 ARGB', 'Refrigeración por Aire Deepcool AG400 ARGB', 26990, 0.00, 11);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('COOLER-LIQUID-MSI-240', 'Refrigeración Líquida MSI MAG CoreLiquid M240 (240mm)', 'Refrigeración Líquida MSI MAG CoreLiquid M240 (240mm)', 79990, 0.05, 11);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('COOLER-LIQUID-NZXT-360', 'Refrigeración Líquida NZXT Kraken 360 RGB Black (360mm)', 'Refrigeración Líquida NZXT Kraken 360 RGB Black (360mm)', 199990, 0.08, 11);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MOUSE-LOGITECH-G203', 'Mouse Gamer Logitech G203 Lightsync Black', 'Mouse Gamer Logitech G203 Lightsync Black', 22990, 0.05, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MOUSE-LOGITECH-G502', 'Mouse Gamer Inalámbrico Logitech G502 LIGHTSPEED', 'Mouse Gamer Inalámbrico Logitech G502 LIGHTSPEED', 89990, 0.08, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MOUSE-RAZER-DEATHADDER', 'Mouse Gamer Razer DeathAdder Essential Black', 'Mouse Gamer Razer DeathAdder Essential Black', 19990, 0.00, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('KEYBOARD-REDRAGON-K552', 'Teclado Mecánico Redragon Kumara K552 RGB (Switch Blue)', 'Teclado Mecánico Redragon Kumara K552 RGB (Switch Blue)', 37990, 0.05, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('KEYBOARD-LOGITECH-G413', 'Teclado Mecánico Logitech G413 TKL SE', 'Teclado Mecánico Logitech G413 TKL SE', 59990, 0.07, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MONITOR-LG-24-144HZ', 'Monitor Gamer LG UltraGear 24" Full HD (144Hz / 1ms)', 'Monitor Gamer LG UltraGear 24" Full HD (144Hz / 1ms)', 149990, 0.10, 7);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('MONITOR-ASUS-27-165HZ', 'Monitor Gamer ASUS TUF Gaming 27" QHD (2K / 165Hz / IPS)', 'Monitor Gamer ASUS TUF Gaming 27" QHD (2K / 165Hz / IPS)', 289990, 0.12, 7);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('AUDIO-HYPERX-CLOUD-FLIGHT', 'Audífonos Gamer Inalámbricos HyperX Cloud Flight Black', 'Audífonos Gamer Inalámbricos HyperX Cloud Flight Black', 84990, 0.05, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('AUDIO-RAZER-BLACKSHARK', 'Audífonos Gamer Razer BlackShark V2 X Black', 'Audífonos Gamer Razer BlackShark V2 X Black', 49990, 0.00, 8);
INSERT INTO products (sku, nombre, descripcion, precio_lista, descuento_efectivo, category_id) VALUES ('CABLE-HDMI-2M', 'Cable HDMI 2.1 2 Metros', 'Cable HDMI 2.1 2 Metros', 7990, 0.00, 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-AMD-R5-5600X', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-AMD-R7-5700X', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-AMD-R7-7800X3D', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-INTEL-I3-12100F', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-INTEL-I5-12400F', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-INTEL-I5-14600K', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CPU-INTEL-I7-14700K', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-NVIDIA-RTX3050', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-NVIDIA-RTX4060', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-NVIDIA-RTX4070-SUPER', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-NVIDIA-RTX4080-SUPER', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-AMD-RX6600', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-AMD-RX7600XT', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'GPU-AMD-RX7800XT', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-KINGSTON-8GB-DDR4', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-KINGSTON-16GB-DDR4', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-CORSAIR-16GB-DDR4', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-CRUCIAL-16GB-DDR5', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-CORSAIR-32GB-DDR5', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'RAM-G_SKILL-32GB-DDR5', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'SSD-KINGSTON-500GB', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'SSD-CRUCIAL-1TB', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'SSD-SAMSUNG-1TB-990', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'SSD-SAMSUNG-2TB-990', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'HDD-SEAGATE-2TB', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MB-ASUS-H610M', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MB-MSI-B550M', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MB-ASUS-B760M', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MB-GIGABYTE-B650', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MB-ASUS-X670E', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'PSU-MSI-550W', 15);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'PSU-EVGA-600W', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'PSU-CORSAIR-650W', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'PSU-GIGABYTE-750W', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'PSU-CORSAIR-850W', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CASE-MSI-FORGE', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CASE-COUGAR-ARCHON', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CASE-LIAN_LI-O11', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'COOLER-DEEPCOOL-AG400', 18);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'COOLER-LIQUID-MSI-240', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'COOLER-LIQUID-NZXT-360', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MOUSE-LOGITECH-G203', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MOUSE-LOGITECH-G502', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MOUSE-RAZER-DEATHADDER', 20);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'KEYBOARD-REDRAGON-K552', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'KEYBOARD-LOGITECH-G413', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MONITOR-LG-24-144HZ', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'MONITOR-ASUS-27-165HZ', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'AUDIO-HYPERX-CLOUD-FLIGHT', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'AUDIO-RAZER-BLACKSHARK', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (1, 'CABLE-HDMI-2M', 22);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-AMD-R5-5600X', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-AMD-R7-5700X', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-AMD-R7-7800X3D', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-INTEL-I3-12100F', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-INTEL-I5-12400F', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-INTEL-I5-14600K', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CPU-INTEL-I7-14700K', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-NVIDIA-RTX3050', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-NVIDIA-RTX4060', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-NVIDIA-RTX4070-SUPER', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-NVIDIA-RTX4080-SUPER', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-AMD-RX6600', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-AMD-RX7600XT', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'GPU-AMD-RX7800XT', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-KINGSTON-8GB-DDR4', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-KINGSTON-16GB-DDR4', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-CORSAIR-16GB-DDR4', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-CRUCIAL-16GB-DDR5', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-CORSAIR-32GB-DDR5', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'RAM-G_SKILL-32GB-DDR5', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'SSD-KINGSTON-500GB', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'SSD-CRUCIAL-1TB', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'SSD-SAMSUNG-1TB-990', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'SSD-SAMSUNG-2TB-990', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'HDD-SEAGATE-2TB', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MB-ASUS-H610M', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MB-MSI-B550M', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MB-ASUS-B760M', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MB-GIGABYTE-B650', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MB-ASUS-X670E', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'PSU-MSI-550W', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'PSU-EVGA-600W', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'PSU-CORSAIR-650W', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'PSU-GIGABYTE-750W', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'PSU-CORSAIR-850W', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CASE-MSI-FORGE', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CASE-COUGAR-ARCHON', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CASE-LIAN_LI-O11', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'COOLER-DEEPCOOL-AG400', 14);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'COOLER-LIQUID-MSI-240', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'COOLER-LIQUID-NZXT-360', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MOUSE-LOGITECH-G203', 14);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MOUSE-LOGITECH-G502', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MOUSE-RAZER-DEATHADDER', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'KEYBOARD-REDRAGON-K552', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'KEYBOARD-LOGITECH-G413', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MONITOR-LG-24-144HZ', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'MONITOR-ASUS-27-165HZ', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'AUDIO-HYPERX-CLOUD-FLIGHT', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'AUDIO-RAZER-BLACKSHARK', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (2, 'CABLE-HDMI-2M', 20);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-AMD-R5-5600X', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-AMD-R7-5700X', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-AMD-R7-7800X3D', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-INTEL-I3-12100F', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-INTEL-I5-12400F', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-INTEL-I5-14600K', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CPU-INTEL-I7-14700K', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-NVIDIA-RTX3050', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-NVIDIA-RTX4060', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-NVIDIA-RTX4070-SUPER', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-NVIDIA-RTX4080-SUPER', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-AMD-RX6600', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-AMD-RX7600XT', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'GPU-AMD-RX7800XT', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-KINGSTON-8GB-DDR4', 14);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-KINGSTON-16GB-DDR4', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-CORSAIR-16GB-DDR4', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-CRUCIAL-16GB-DDR5', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-CORSAIR-32GB-DDR5', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'RAM-G_SKILL-32GB-DDR5', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'SSD-KINGSTON-500GB', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'SSD-CRUCIAL-1TB', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'SSD-SAMSUNG-1TB-990', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'SSD-SAMSUNG-2TB-990', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'HDD-SEAGATE-2TB', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MB-ASUS-H610M', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MB-MSI-B550M', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MB-ASUS-B760M', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MB-GIGABYTE-B650', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MB-ASUS-X670E', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'PSU-MSI-550W', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'PSU-EVGA-600W', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'PSU-CORSAIR-650W', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'PSU-GIGABYTE-750W', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'PSU-CORSAIR-850W', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CASE-MSI-FORGE', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CASE-COUGAR-ARCHON', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CASE-LIAN_LI-O11', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'COOLER-DEEPCOOL-AG400', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'COOLER-LIQUID-MSI-240', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'COOLER-LIQUID-NZXT-360', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MOUSE-LOGITECH-G203', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MOUSE-LOGITECH-G502', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MOUSE-RAZER-DEATHADDER', 14);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'KEYBOARD-REDRAGON-K552', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'KEYBOARD-LOGITECH-G413', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MONITOR-LG-24-144HZ', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'MONITOR-ASUS-27-165HZ', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'AUDIO-HYPERX-CLOUD-FLIGHT', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'AUDIO-RAZER-BLACKSHARK', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (3, 'CABLE-HDMI-2M', 18);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-AMD-R5-5600X', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-AMD-R7-5700X', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-AMD-R7-7800X3D', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-INTEL-I3-12100F', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-INTEL-I5-12400F', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-INTEL-I5-14600K', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CPU-INTEL-I7-14700K', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-NVIDIA-RTX3050', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-NVIDIA-RTX4060', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-NVIDIA-RTX4070-SUPER', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-NVIDIA-RTX4080-SUPER', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-AMD-RX6600', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-AMD-RX7600XT', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'GPU-AMD-RX7800XT', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-KINGSTON-8GB-DDR4', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-KINGSTON-16GB-DDR4', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-CORSAIR-16GB-DDR4', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-CRUCIAL-16GB-DDR5', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-CORSAIR-32GB-DDR5', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'RAM-G_SKILL-32GB-DDR5', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'SSD-KINGSTON-500GB', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'SSD-CRUCIAL-1TB', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'SSD-SAMSUNG-1TB-990', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'SSD-SAMSUNG-2TB-990', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'HDD-SEAGATE-2TB', 12);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MB-ASUS-H610M', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MB-MSI-B550M', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MB-ASUS-B760M', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MB-GIGABYTE-B650', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MB-ASUS-X670E', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'PSU-MSI-550W', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'PSU-EVGA-600W', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'PSU-CORSAIR-650W', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'PSU-GIGABYTE-750W', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'PSU-CORSAIR-850W', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CASE-MSI-FORGE', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CASE-COUGAR-ARCHON', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CASE-LIAN_LI-O11', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'COOLER-DEEPCOOL-AG400', 11);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'COOLER-LIQUID-MSI-240', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'COOLER-LIQUID-NZXT-360', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MOUSE-LOGITECH-G203', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MOUSE-LOGITECH-G502', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MOUSE-RAZER-DEATHADDER', 15);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'KEYBOARD-REDRAGON-K552', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'KEYBOARD-LOGITECH-G413', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MONITOR-LG-24-144HZ', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'MONITOR-ASUS-27-165HZ', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'AUDIO-HYPERX-CLOUD-FLIGHT', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'AUDIO-RAZER-BLACKSHARK', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (4, 'CABLE-HDMI-2M', 16);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-AMD-R5-5600X', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-AMD-R7-5700X', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-AMD-R7-7800X3D', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-INTEL-I3-12100F', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-INTEL-I5-12400F', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-INTEL-I5-14600K', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CPU-INTEL-I7-14700K', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-NVIDIA-RTX3050', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-NVIDIA-RTX4060', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-NVIDIA-RTX4070-SUPER', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-NVIDIA-RTX4080-SUPER', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-AMD-RX6600', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-AMD-RX7600XT', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'GPU-AMD-RX7800XT', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-KINGSTON-8GB-DDR4', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-KINGSTON-16GB-DDR4', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-CORSAIR-16GB-DDR4', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-CRUCIAL-16GB-DDR5', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-CORSAIR-32GB-DDR5', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'RAM-G_SKILL-32GB-DDR5', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'SSD-KINGSTON-500GB', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'SSD-CRUCIAL-1TB', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'SSD-SAMSUNG-1TB-990', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'SSD-SAMSUNG-2TB-990', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'HDD-SEAGATE-2TB', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MB-ASUS-H610M', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MB-MSI-B550M', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MB-ASUS-B760M', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MB-GIGABYTE-B650', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MB-ASUS-X670E', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'PSU-MSI-550W', 8);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'PSU-EVGA-600W', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'PSU-CORSAIR-650W', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'PSU-GIGABYTE-750W', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'PSU-CORSAIR-850W', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CASE-MSI-FORGE', 6);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CASE-COUGAR-ARCHON', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CASE-LIAN_LI-O11', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'COOLER-DEEPCOOL-AG400', 10);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'COOLER-LIQUID-MSI-240', 9);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'COOLER-LIQUID-NZXT-360', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MOUSE-LOGITECH-G203', 13);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MOUSE-LOGITECH-G502', 4);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MOUSE-RAZER-DEATHADDER', 14);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'KEYBOARD-REDRAGON-K552', 3);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'KEYBOARD-LOGITECH-G413', 5);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MONITOR-LG-24-144HZ', 2);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'MONITOR-ASUS-27-165HZ', 0);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'AUDIO-HYPERX-CLOUD-FLIGHT', 7);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'AUDIO-RAZER-BLACKSHARK', 1);
INSERT INTO inventory (branch_id, sku, cantidad) VALUES (5, 'CABLE-HDMI-2M', 16);

COMMIT;
