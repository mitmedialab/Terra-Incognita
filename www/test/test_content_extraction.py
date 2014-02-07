from boilerpipe.extract import Extractor

extractor = Extractor(extractor='ArticleExtractor', url='http://www.nickdiakopoulos.com/2013/08/01/sex-violence-and-autocomplete-algorithms-methods-and-context/')
extracted_text = extractor.getText()

print extracted_text
print "LOOKS LIKE A SUCCESS!"
