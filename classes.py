class Posting:
    def __init__(self, id, frequency):
        self.docID = id
        self.token_frequency = frequency
        self.tf_idf_score = 0
    def __eq__(self,other):
        return self.docID == other.docID
    def __ne__(self,other):
        return self.docID != other.docID
    def __gt__(self,other): 
        return self.docID > other.docID
    def __lt__(self,other):
        return self.docID < other.docID
    def __str__(self):
        return f'docId: {self.docID}, token_frequency: {self.token_frequency}, tf_idf: {self.tf_idf_score}'
    def __repr__(self):
        return f'docId: {self.docID}, token_frequency: {self.token_frequency}, tf_idf: {self.tf_idf_score}' + '\n'

"""
Structure of the Inverted Index
{ 
    Token : {
        token_frequency: int
        document_frequency: int
        doc_ids: {
            id1: Posting
            id2: Posting
    }
}
"""
    