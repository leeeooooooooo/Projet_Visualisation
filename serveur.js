const jsonServer = require('json-server');
const server = jsonServer.create();
const router = jsonServer.router('db.json');
const middlewares = jsonServer.defaults();
const bodyParser = require('body-parser');
const jwt = require('jsonwebtoken');

const JWT_SECRET = 'monsecret123';

server.use(middlewares);
server.use(bodyParser.json());

// 🚀 Route de connexion personnalisée
server.post('/login', (req, res) => {
  const db = router.db; // lowdb instance
  const { Identifiant, Numero_Emplacement, Mot_de_passe } = req.body;

  let user = null;

  if (Identifiant) {
    user = db.get('gerants').find({ Identifiant, Mot_de_passe }).value();
  } else if (Numero_Emplacement) {
    user = db.get('campeurs').find({ Numero_Emplacement, Mot_de_passe }).value();
  }

  if (user) {
    const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
    return res.json({ token, role: user.role });
  } else {
    return res.status(401).json({ message: 'Identifiants incorrects' });
  }
});

server.use(router);

// Démarrage
server.listen(3003, () => {
  console.log('JSON Server est lancé sur http://localhost:3003');
});
