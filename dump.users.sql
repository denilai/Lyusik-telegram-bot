PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "guests" (id integer primary key, name text);
INSERT INTO guests VALUES(1,'Natasha');
INSERT INTO guests VALUES(2,'Dasha');
CREATE TABLE questions (
  question_id integer primary key autoincrement, 
  question_text text not null,
  right_answer text not null
);
INSERT INTO questions VALUES(1,'В какой стране родился Арнольд Шварцнеггер?','Австрия');
INSERT INTO questions VALUES(2,'Сколько граммов в килограмме?','1000');
INSERT INTO questions VALUES(3,'Какого цвета маслины?','Черного');
CREATE TABLE user_stat (
  id integer not null references users(user_id) on delete cascade on update cascade,
  question_id not null references questions(question_id) on delete cascade on update cascade,
  answer_text text not null,
  right  boolean not null
);
CREATE TABLE wrong_answers (
  answer_id integer primary key,
  question_id integer not null references squestions(question_id) on delete cascade on update cascade,
  answer_text text not null
);
INSERT INTO wrong_answers VALUES(1,2,'200');
INSERT INTO wrong_answers VALUES(2,2,'90');
INSERT INTO wrong_answers VALUES(3,3,'Желтого');
INSERT INTO wrong_answers VALUES(4,3,'Зеленого');
INSERT INTO wrong_answers VALUES(5,1,'Россия');
INSERT INTO wrong_answers VALUES(6,1,'Америка');
INSERT INTO wrong_answers VALUES(7,1,'Австралия');
CREATE TABLE users (
user_id integer primary key not null,
name text not null);
INSERT INTO users VALUES(1,'Наташа');
INSERT INTO users VALUES(2,'Даша');
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('questions',3);
COMMIT;
