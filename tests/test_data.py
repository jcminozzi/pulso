import unittest
from app import analyze,clean_rows,facts_from,validate_notes

def row(**changes):
    value={'order_id':'V001','date':'2026-01-05','category':'Livros','quantity':'2','unit_price':'19.90','status':'concluida'}
    value.update(changes);return value

class DataTests(unittest.TestCase):
    def test_exact_money_and_units(self):
        rows,errors=clean_rows([row()]);result=analyze(rows)
        self.assertEqual(errors,[]);self.assertEqual(result['summary']['revenue_cents'],3980)
        self.assertEqual(result['summary']['units'],2)
    def test_cancelled_orders_do_not_inflate_revenue(self):
        rows,_=clean_rows([row(),row(order_id='V002',status='cancelada')]);s=analyze(rows)['summary']
        self.assertEqual(s['completed_orders'],1);self.assertEqual(s['cancelled_orders'],1)
        self.assertEqual(s['revenue_cents'],3980)
    def test_duplicates_go_to_review(self):
        clean,errors=clean_rows([row(),row()]);self.assertEqual(len(clean),1);self.assertEqual(len(errors),1)
    def test_bad_dates_and_amounts_go_to_review(self):
        for changes in ({'date':'2026-02-30'},{'quantity':'-1'},{'unit_price':'NaN'},{'unit_price':'19,90'},{'status':'outro'}):
            with self.subTest(changes=changes):self.assertEqual(len(clean_rows([row(**changes)])[1]),1)
    def test_category_and_month_aggregation(self):
        rows,_=clean_rows([row(),row(order_id='V002',category='Papelaria',date='2026-02-01')])
        result=analyze(rows);self.assertEqual(len(result['by_category']),2);self.assertEqual(len(result['by_month']),2)
    def test_empty_dataset_is_well_defined(self):
        self.assertEqual(analyze([])['summary']['revenue_cents'],0)
    def test_sql_special_characters_are_data(self):
        rows,_=clean_rows([row(category="Livros'; DROP TABLE sales;--")])
        self.assertEqual(analyze(rows)['summary']['completed_orders'],1)
    def test_ai_evidence_must_match_computed_facts(self):
        rows,_=clean_rows([row()]);facts=facts_from(analyze(rows))
        notes={'observations':[{'fact_id':'revenue','evidence':facts['revenue'],'comment':'A receita soma os pedidos concluídos.'}],'questions':[]}
        self.assertIs(validate_notes(notes,facts),notes)
        notes['observations'][0]['evidence']='Receita de R$ 1 milhão'
        with self.assertRaises(ValueError):validate_notes(notes,facts)
    def test_ai_cannot_reference_unknown_metric(self):
        with self.assertRaises(ValueError):validate_notes({'observations':[{'fact_id':'lucro','evidence':'100','comment':'x'}],'questions':[]},{'revenue':'1'})

if __name__=='__main__':unittest.main()
