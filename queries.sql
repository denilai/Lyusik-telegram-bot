create table if not exists questions (
  question_id integer primary key, 
  question_text text not null,
  right_answer text not null,
  location text not null
);
create table if not exists wrong_answers (
  answer_id integer primary key,
  question_id integer not null references questions(question_id) on delete cascade on update cascade,
  answer_text text not null
);

create table if not exists users (
  user_id integer not null,
  name text not null 
);

create table if not exists location_question (
  question_id integer not null references questions(question_id) on delete cascade on update cascade,
  location text not null
);

insert into location_question values (1,'diller'),(2,'chemists'), (3,'shtirlez');

--create table if not exists user_stat (
--  id integer not null references users(user_id) on delete cascade on update cascade,
--  question_id not null references questions(question_id) on delete cascade on update cascade,
--  answer_text text not null,
--  right  boolean not null
--);


create table if not exists media_ids (
  id integer not null primary key,
  file_id string,
  filename string,
  file_type  string
);

create table if not exists question_media (
  id integer not null primary key, 
  question_id integer not null references question(question_id) on delete cascade on update cascade,
  media_type string not null, 
  filename text not null references media_ids(filename) on delete cascade on update cascade,
  check (media_type  in ('photo', 'audio', 'file', 'video'))
);

create table if not exists answer_media (
  id integer not null primary key, 
  question_id integer not null references question(question_id) on delete cascade on update cascade,
  media_type string not null, 
  filename text not null references media_ids(filename) on delete cascade on update cascade,
  check (media_type  in ('photo', 'audio', 'file', 'video'))
);


create table if not exists log (
  id integer not null primary key,  
  timestamp timestamp, 
  user_id integer,
  user text,  
  question text, 
  answer text,
  is_right boolean
);

--insert into questions (question_text, right_answer, location) values 
--("В какой стране родился Арнольд Шварцнеггер?", "Австрия", "diller"),
--("Сколько граммов в килограмме?","1000","diller"),
--("Какого цвета маслины?","Черного", "chemist"),
--("Кто убил Марка?", "Оксимирон", "shtirlez")

--insert into wrong_answers (question_id, answer_text) values 
--(1,  "Россия"),
--(1, "Америка"),
--(1, "Австралия");
--(2, "200"),
--(2,"90"),
--(3,"Желтого"),
--(3,"Зеленого"),
--(4,"Алиса"),
--(4,"Мэр");


--insert into users (name) values ("Наташа"), ("Даша");

--insert into question_media (question_id, media_type, filename) values
--(1, 'photo', 'zima.jpg'),
--(1, 'photo', 'botavatar.jpg'),
--(3, 'video', 'piter.mov');


--insert into answer_media (question_id, media_type, filename) values
--(1, 'photo', 'zima.jpg'),
--(1, 'photo', 'botavatar.jpg'),
--(3, 'video', 'piter.mov');

insert into questions (question_text, right_answer, location) values
--('Вспомни тусовку, на которой вы менялись штанами с Дашей, Кубой и Данилой. Кто чьи штаны взял?','Данила поменялся с Наташей, Куба поменялся с Дашей', 'garage'),
--('Перед тобой видеофрагмент. Вспомни, какая фраза была следующей.', '... иди в жопу!','garage'),
--('Перед тобой несколько фотографий. Вспомни, после просмотра какого видео вы с Дашей так сильно смеялись.','Парень из видео скинул из штанины бомбу в магазине','chemist'),
--('Как называется придорожное кафе, в котором вы едите по дороге в Тамбов?','Робин Сдобин','diler'),
--('Кто поцарапал машину Данилы Бунина в поле?','Никто','father'),
--('Песня какого исполнителя является гимном комнаты 602А в общежитии РТУ МИРЭА на Юго-Западной?','Jamik','diler'),
--('Как правильно называется кофейный напиток, приготавливаемый путём вливания в молоко кофе-эспрессо в пропорции 3:1?','Латте макиато', 'diler'),
--('Какого ингредиента не было в рецепте фирменного плова из видео?','Рис','chemist'),
--('С обсуждения какой темы вы начали разговор с Димой при первой встрече?','Аниме-сериал "Евангелион"','shtirliz'),
--('Как звали солиста группы, с которым вас с Дианой сфотографировал Дима в августе 2018 года?','Максим','shtirliz'),
--('В чем особенность поведения Ильи по прозвищу "Малой"?','Все из вышеперечисленного','father'),
--('Как зовут одного из лучших друзей Кирилла, который носит очки, и с которым ты познакомилась в Алтуфьево?','Ярослав','father');
