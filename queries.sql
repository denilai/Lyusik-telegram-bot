create table if not exists questions (
  question_id integer primary key, 
  question_text text not null,
  right_answer text not null
);
create table if not exists wrong_answers (
  answer_id integer primary key,
  question_id integer not null references squestions(question_id) on delete cascade on update cascade,
  answer_text text not null
);

create table if not exists users (
  user_id integer not null,
  name text not null 
);

create table if not exists user_stat (
  id integer not null references users(user_id) on delete cascade on update cascade,
  question_id not null references questions(question_id) on delete cascade on update cascade,
  answer_text text not null,
  right  boolean not null
);


--insert into questions (question_text, right_answer) values 
--("В какой стране родился Арнольд Шварцнеггер?", "Австрия"),
--("Сколько граммов в килограмме?","1000"),
--("Какого цвета маслины?","Черного");

--insert into wrong_answers (question_id, answer_text) values 
--(1,  "Россия"),
--(1, "Америка"),
--(1, "Австралия");
--(2, "200"),
--(2,"90"),
--(3,"Желтого"),
--(3,"Зеленого");


--insert into users (name) values ("Наташа"), ("Даша");


