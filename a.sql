select question_text, right_answer from (select row_number() over(order by question_id) rn, * from questions where location = 'diller') where rn = 1
