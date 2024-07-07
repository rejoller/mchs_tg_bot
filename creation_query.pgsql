CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    user_name TEXT,
    last_name TEXT,
    username TEXT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)



CREATE TABLE municipalities (
    map_id VARCHAR(10) UNIQUE NOT NULL,
    municipality_name VARCHAR(50) 
)



INSERT INTO municipalities (map_id, municipality_name)
VALUES 
('id48', 'город Ачинск'),
('id41', 'город Боготол'),
('id42', 'город Бородино'),
('id44', 'город Дивногорск'),
('id19', 'город Енисейск'),
('id57', 'город Канск'),
('id39', 'поселок Кедровый'),
('id17', 'город Красноярск'),
('id51', 'город Лесосибирск'),
('id20', 'город Минусинск'),
('id45', 'город Назарово'),
('id52', 'город Норильск'),
('id37', 'город Сосновоборск'),
('id60', 'город Шарыпово'),
('id38', 'ЗАТО город Железногорск'),
('id53', 'ЗАТО город Зеленогорск'),
('id8', 'ЗАТО поселок Солнечный'),
('id1', 'Абанский район'),
('id59', 'Ачинский район'),
('id2', 'Балахтинский район'),
('id43', 'Березовский район'),
('id4', 'Бирилюсский район'),
('id46', 'Боготольский район'),
('id5', 'Богучанский район'),
('id6', 'Большемуртинский район'),
('id7', 'Большеулуйский район'),
('id3', 'Дзержинский район'),
('id47', 'Емельяновский район'),
('id54', 'Енисейский район'),
('id9', 'Ермаковский район'),
('id10', 'Идринский район'),
('id55', 'Иланский район'),
('id11', 'Ирбейский район'),
('id12', 'Казачинский район'),
('id56', 'Канский район'),
('id14', 'Каратузский район'),
('id15', 'Кежемский район'),
('id16', 'Козульский район'),
('id13', 'Краснотуранский район'),
('id18', 'Курагинский район'),
('id21', 'Манский район'),
('id22', 'Минусинский район'),
('id24', 'Мотыгинский район'),
('id50', 'Назаровский район'),
('id25', 'Нижнеингашский район'),
('id23', 'Новоселовский район'),
('id26', 'Партизанский район'),
('id27', 'Пировский муниципальный округ'),
('id49', 'Рыбинский район'),
('id29', 'Саянский район'),
('id32', 'Северо-Енисейский район'),
('id28', 'Сухобузимский район'),
('id40', 'Таймырский Долгано-Ненецкий муниципальный район'),
('id30', 'Тасеевский район'),
('id31', 'Туруханский район'),
('id33', 'Тюхтетский муниципальный округ'),
('id58', 'Ужурский район'),
('id34', 'Уярский район'),
('id35', 'Шарыповский муниципальный округ'),
('id36', 'Шушенский район'),
('id0', 'Эвенкийский муниципальный район');



CREATE TABLE subscriptions (
    user_id BIGINT REFERENCES users(user_id),
    map_id VARCHAR(10) REFERENCES municipalities(map_id),
    municipality_name VARCHAR(50) REFERENCES municipalities(municipality_name),
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE subscriptions
ADD COLUMN id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY;
