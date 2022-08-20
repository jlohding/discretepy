from truth_table import TruthTable, StatementBuilder

if __name__ == "__main__":
    '''Sample usage of the TruthTable api
    '''

    tt = TruthTable("P", "Q")

    sb = StatementBuilder()
    not_Q = sb.get_statement("NOT", params=["Q"]) # not Q 
    P_or_Q = sb.get_statement("IDENTITY", "OR", "IDENTITY", params=[["P"], ["Q"]]) # P OR Q
    PorQ_and_notQ = sb.get_statement(P_or_Q, "AND", not_Q, params=[
                                                                [["P"], ["Q"]],
                                                                ["Q"],
                                                            ]) # [ (P OR Q) AND notQ ]
    PorQ_and_notQ__impliesP = sb.get_statement(PorQ_and_notQ, "->", "IDENTITY", params=[
                                                                                        [
                                                                                            [["P"], ["Q"]],
                                                                                            ["Q"],
                                                                                        ],
                                                                                        ["P"],
                                                                                    ]) # [ (P OR Q) AND notQ ] -> P, which is a tautology
                                                                                    
    tt.add_statement(not_Q) \
        .add_statement(P_or_Q) \
        .add_statement(PorQ_and_notQ) \
        .add_statement(PorQ_and_notQ__impliesP)

    table = tt.get_truth_table()
    print(table)