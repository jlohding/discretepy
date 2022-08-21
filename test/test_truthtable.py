from src.truthtable.truth_table import TruthTable, StatementBuilder
import unittest
import pandas as pd


class TestTruthTable(unittest.TestCase):
    def setUp(self):
        self.sb = StatementBuilder()

    def test_init_TruthTable(self):
        tt = TruthTable("A", "B")
        df = pd.DataFrame([
                [True, True],
                [True, False],
                [False, True],
                [False, False],
            ], columns=["A", "B"]
        )
        pd.testing.assert_frame_equal(tt.get_truth_table(), df, "incorrect boolean permutations")

    def test_logic(self):
        # Q
        P = self.sb.get_statement("IDENTITY", params=["P"])
        Q = self.sb.get_statement("IDENTITY", params=["Q"])
        self.assertTrue(Q.compute(True))
        self.assertFalse(Q.compute(False))

        # not Q
        not_Q = self.sb.get_statement("NOT", params=["Q"])
        self.assertTrue(not_Q.compute(False))
        self.assertFalse(not_Q.compute(True))

        # P & Q
        P_and_Q = self.sb.get_statement(P, "AND", Q, params=[["P"], ["Q"]])
        self.assertTrue(P_and_Q.compute([True], [True]))
        self.assertFalse(P_and_Q.compute([True], [False]))
        self.assertFalse(P_and_Q.compute([False], [True]))        
        self.assertFalse(P_and_Q.compute([False], [False]))

        # P | Q
        P_or_Q = self.sb.get_statement(P, "OR", Q, params=[["P"], ["Q"]])
        self.assertTrue(P_or_Q.compute([True], [True]))
        self.assertTrue(P_or_Q.compute([True], [False]))
        self.assertTrue(P_or_Q.compute([False], [True]))        
        self.assertFalse(P_or_Q.compute([False], [False]))

        # P ^ Q
        P_xor_Q = self.sb.get_statement(P, "XOR", Q, params=[["P"], ["Q"]])
        self.assertFalse(P_xor_Q.compute([True], [True]))
        self.assertTrue(P_xor_Q.compute([True], [False]))
        self.assertTrue(P_xor_Q.compute([False], [True]))        
        self.assertFalse(P_xor_Q.compute([False], [False]))

        # P -> Q 
        P_implies_Q = self.sb.get_statement(P, "->", Q, params=[["P"], ["Q"]])
        self.assertTrue(P_implies_Q.compute([True], [True]))
        self.assertFalse(P_implies_Q.compute([True], [False]))
        self.assertTrue(P_implies_Q.compute([False], [True]))        
        self.assertTrue(P_implies_Q.compute([False], [False]))

        # P <-> Q 
        P_equivalent_Q = self.sb.get_statement(P, "<->", Q, params=[["P"], ["Q"]])
        self.assertTrue(P_equivalent_Q.compute([True], [True]))
        self.assertFalse(P_equivalent_Q.compute([True], [False]))
        self.assertFalse(P_equivalent_Q.compute([False], [True]))        
        self.assertTrue(P_equivalent_Q.compute([False], [False]))

    def test_complex_logic(self):
        P = self.sb.get_statement("IDENTITY", params=["P"]) 
        Q = self.sb.get_statement("IDENTITY", params=["Q"]) 
        not_Q = self.sb.get_statement("NOT", params=["Q"])
        P_or_Q = self.sb.get_statement(P, "OR", Q, params=[["P"], ["Q"]])

        # (P | Q) & not_Q
        PorQ_and_notQ = self.sb.get_statement(P_or_Q, "AND", not_Q, params=[[["P"], ["Q"]], ["Q"]])
        self.assertFalse(PorQ_and_notQ.compute([[True], [True]], [True]))
        self.assertTrue(PorQ_and_notQ.compute([[True], [False]], [False]))
        self.assertFalse(PorQ_and_notQ.compute([[False], [True]], [True]))
        self.assertFalse(PorQ_and_notQ.compute([[False], [False]], [False]))

        #[(P OR Q) & not_Q] -> P (tautology)
        PorQ_and_notQ__impliesP = self.sb.get_statement(PorQ_and_notQ, "->", "IDENTITY", params=[[
                                                                                        [["P"], ["Q"]], ["Q"]],
                                                                                        ["P"]])
        self.assertTrue(PorQ_and_notQ__impliesP.compute([[[True], [True]], [True]],[True]))
        self.assertTrue(PorQ_and_notQ__impliesP.compute([[[True], [False]], [False]],[True]))
        self.assertTrue(PorQ_and_notQ__impliesP.compute([[[False], [True]], [True]],[False]))
        self.assertTrue(PorQ_and_notQ__impliesP.compute([[[False], [False]], [False]],[False]))
    
    def test_get_truth_table(self):
        tt = TruthTable("P", "Q", "R", "S", "T")

        # P | S
        statement = self.sb.get_statement("IDENTITY", "OR", "IDENTITY", params=[["P"], ["S"]])
        tt.add_statement(statement)

        table = tt.get_truth_table()
        self.assertEquals(table.shape, (32,6)) # table shape should be (2^5, 5+1)