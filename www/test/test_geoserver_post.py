# coding=utf-8
import requests

text = u'db.collection.find() — MongoDB Manual 2.6.0 criteria document Optional. Specifies selection criteria using query operators . To return all documents in a collection, omit this parameter or pass an empty document ({}). projection document Optional. Specifies the fields to return using projection operators . To return all fields in the matching document, omit this parameter. Returns: A cursor to the documents that match the query criteria. When the find() method “returns documents,” the method is actually returning a cursor to the documents. If the projection argument is specified, the matching documents contain only the projection fields and the _id field. You can optionally exclude the _id field. Executing find() directly in the mongo shell automatically iterates the cursor to display up to the first 20 documents. Type it to continue iteration. To access the returned documents with a driver, use the appropriate cursor handling mechanism for the driver language . The projection parameter takes a document of the following form: { field1: <boolean>, field2: <boolean> ... } The <boolean> value can be any of the following: 1 or true to include the field. The find() method always includes the _id field even if the field is not explicitly stated to return in the projection parameter. 0 or false to exclude the field. A projection cannot contain both include and exclude specifications, except for the exclusion of the _id field. In projections that explicitly include fields, the _id field is the only field that you can explicitly exclude. db.collection.find() is a wrapper for the more formal query structure that uses the $query operator. Examples ¶ Find All Documents in a Collection ¶ The find() method with no parameters returns all documents from a collection and returns all fields for the documents. For example, the following operation returns all documents in the bios collection : db.bios.find() Find Documents that Match Query Criteria ¶ To find documents that match a set of selection criteria, call find() with the <criteria> parameter. The following operation returns all the documents from the collection products where qty is greater than 25: db.products.find( { qty: { $gt: 25 } } ) The following operation returns documents in the bios collection where _id equals 5: db.bios.find( { _id: 5 } ) Query Using Operators ¶ The following operation returns documents in the bios collection where _id equals either 5 or ObjectId(\"507c35dd8fada716c89d0013\"): db.bios.find( { _id: { $in: [ 5, ObjectId(\"507c35dd8fada716c89d0013\") ] } } ) Query for Ranges ¶ Combine comparison operators to specify ranges. The following operation returns documents with field between value1 and value2: db.collection.find( { field: { $gt: value1, $lt: value2 } } ); Query a Field that Contains an Array ¶ If a field contains an array and your query has multiple conditional operators, the field as a whole will match if either a single array element meets the conditions or a combination of array elements meet the conditions. Given a collection students that contains the following documents: { \"_id\" : 1, \"score\" : [ -1, 3 ] } { \"_id\" : 2, \"score\" : [ 1, 5 ] } { \"_id\" : 3, \"score\" : [ 5, 5 ] } The following query: db.students.find( { score: { $gt: 0, $lt: 2 } } ) Matches the following documents: { \"_id\" : 1, \"score\" : [ -1, 3 ] } { \"_id\" : 2, \"score\" : [ 1, 5 ] } In the document with _id equal to 1, the score: [ -1, 3 ] meets the conditions because the element -1 meets the $lt: 2 condition and the element 3 meets the $gt: 0 condition. In the document with _id equal to 2, the score: [ 1, 5 ] meets the conditions because the element 1 meets both the $lt: 2 condition and the $gt: 0 condition. Query Arrays ¶ Query for an Array Element ¶ The following operation returns documents in the bios collection where the array field contribs contains the element \"UNIX\": db.bios.find( { contribs: \"UNIX\" } ) Query an Array of Documents ¶ The following operation returns documents in the bios collection where awards array contains a subdocument element that contains the award field equal to \"Turing Award\" and the year field greater than 1980: db.bios.find( { awards: { $elemMatch: { award: \"Turing Award\", year: { $gt: 1980 } } } } ) Query Subdocuments ¶ Query Exact Matches on Subdocuments ¶ The following operation returns documents in the bios collection where the subdocument name is exactly { first: \"Yukihiro\", last: \"Matsumoto\" }, including the order: db.bios.find( { name: { first: \"Yukihiro\", last: \"Matsumoto\" } } ) The name field must match the sub-document exactly. The query does not match documents with the following name fields: { first: \"Yukihiro\", aka: \"Matz\", last: \"Matsumoto\" } { last: \"Matsumoto\", first: \"Yukihiro\" } Query Fields of a Subdocument ¶ The following operation returns documents in the bios collection where the subdocument name contains a field first with the value \"Yukihiro\" and a field last with the value \"Matsumoto\". The query uses dot notation to access fields in a subdocument: db.bios.find( { \"name.first\": \"Yukihiro\", \"name.last\": \"Matsumoto\" } ) The query matches the document where the name field contains a subdocument with the field first with the value \"Yukihiro\" and a field last with the value \"Matsumoto\". For instance, the query would match documents with name fields that held either of the following values: { first: \"Yukihiro\", aka: \"Matz\", last: \"Matsumoto\" } { last: \"Matsumoto\", first: \"Yukihiro\" } Projections ¶ The projection parameter specifies which fields to return. The parameter contains either include or exclude specifications, not both, unless the exclude is for the _id field. Specify the Fields to Return ¶ The following operation returns all the documents from the products collection where qty is greater than 25 and returns only the _id, item and qty fields: db.products.find( { qty: { $gt: 25 } }, { item: 1, qty: 1 } ) The operation returns the following: { \"_id\" : 11, \"item\" : \"pencil\", \"qty\" : 50 } { \"_id\" : ObjectId(\"50634d86be4617f17bb159cd\"), \"item\" : \"bottle\", \"qty\" : 30 } { \"_id\" : ObjectId(\"50634dbcbe4617f17bb159d0\"), \"item\" : \"paper\", \"qty\" : 100 } The following operation finds all documents in the bios collection and returns only the name field, contribs field and _id field: db.bios.find( { }, { name: 1, contribs: 1 } ) Explicitly Excluded Fields ¶ The following operation queries the bios collection and returns all fields except the the first field in the name subdocument and the birth field: db.bios.find( { contribs: \'OOP\' }, { \'name.first\': 0, birth: 0 } ) Explicitly Exclude the _id Field ¶ The following operation excludes the _id and qty fields from the result set: db.products.find( { qty: { $gt: 25 } }, { _id: 0, qty: 0 } ) The documents in the result set contain all fields except the _id and qty fields: { \"item\" : \"pencil\", \"type\" : \"no.2\" } { \"item\" : \"bottle\", \"type\" : \"blue\" } { \"item\" : \"paper\" } The following operation finds documents in the bios collection and returns only the name field and the contribs field: db.bios.find( { }, { name: 1, contribs: 1, _id: 0 } ) On Arrays and Subdocuments ¶ The following operation queries the bios collection and returns the last field in the name subdocument and the first two elements in the contribs array: db.bios.find( { }, { _id: 0, \'name.last\': 1, contribs: { $slice: 2 } } ) Iterate the Returned Cursor ¶ The find() method returns a cursor to the results. In the mongo shell, if the returned cursor is not assigned to a variable using the var keyword, the cursor is automatically iterated up to 20 times to access up to the first 20 documents that match the query. You can use the DBQuery.shellBatchSize to change the number of iterations. See Flags and Cursor Behaviors . To iterate manually, assign the returned cursor to a variable using the var keyword. With Variable Name ¶ The following example uses the variable myCursor to iterate over the cursor and print the matching documents: var myCursor = db.bios.find( ); myCursor The following example uses the cursor method next() to access the documents: var myCursor = db.bios.find( ); var myDocument = myCursor.hasNext() ? myCursor.next() : null; if (myDocument) { var myName = myDocument.name; print (tojson(myName)); } To print, you can also use the printjson() method instead of print(tojson()): if (myDocument) { var myName = myDocument.name; printjson(myName); } With forEach() Method ¶ The following example uses the cursor method forEach() to iterate the cursor and access the documents: var myCursor = db.bios.find( ); myCursor.forEach(printjson); Modify the Cursor Behavior ¶ The mongo shell and the drivers provide several cursor methods that call on the cursor returned by the find() method to modify its behavior. Order Documents in the Result Set ¶ The sort() method orders the documents in the result set. The following operation returns documents in the bios collection sorted in ascending order by the name field: db.bios.find().sort( { name: 1 } ) sort() corresponds to the ORDER BY statement in SQL. Limit the Number of Documents to Return ¶ The limit() method limits the number of documents in the result set. The following operation returns at most 5 documents in the bios collection : db.bios.find().limit( 5 ) limit() corresponds to the LIMIT statement in SQL. Set the Starting Point of the Result Set ¶ The skip() method controls the starting point of the results set. The following operation skips the first 5 documents in the bios collection and returns all remaining documents: db.bios.find().skip( 5 ) The following example chains cursor methods: db.bios.find().sort( { name: 1 } ).limit( 5 ) db.bios.find().limit( 5 ).sort( { name: 1 } ) Regardless of the order you chain the limit() and the sort() , the request to the server has the structure that treats the query and the sort() modifier as a single object. Therefore, the limit() operation method is always applied after the sort() regardless of the specified order of the operations in the chain. See the meta query operators . Copyright © 2011-2014 MongoDB, Inc . Licensed under Creative Commons . MongoDB, Mongo, and the leaf logo are registered trademarks of MongoDB, Inc. ON THIS PAGE'

params = {'q':text}
		
r = requests.post('http://localhost:8080/CLIFF/parse/text', params=params)
print r
print r.json()