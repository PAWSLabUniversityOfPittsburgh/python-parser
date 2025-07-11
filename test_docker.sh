
curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"import txt"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"import txt\ntest=1"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"s='hola'"}'

curl -X POST http://127.0.0.1:13456/extract_concepts -H "Content-Type: application/json" -d '{"code_str":"s='hola'\ns[0:2]"}'