module.exports = {
    transform: {
      '^.+\\.js$': 'babel-jest',  // Transformation des fichiers .js avec babel
    },
    testEnvironment: 'jsdom',
    transformIgnorePatterns: ['/node_modules/(?!@vue)'],  // Ne pas ignorer les packages Vue
    moduleFileExtensions: ['js', 'vue', 'json'],
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],  // Si tu as un fichier de setup Jest
  };
  