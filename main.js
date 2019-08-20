const electron = require('electron');
const app = electron.app;
const BrowserWindow = electron.BrowserWindow;


var mainWindow = null;

app.on('window-all-closed', function() {
  //if (process.platform != 'darwin') {
    app.quit();
  //}
});

app.on('ready', function() {
  // call python?
  var subpy = require('child_process').spawn('python', ['./hello.py']);
  //var subpy = require('child_process').spawn('./dist/hello.exe');
  var rq = require('request-promise');
  var mainAddr = 'http://127.0.0.1:5000';

  var openWindow = function(){
    mainWindow = new BrowserWindow({width: 1000, height:800});
    // mainWindow.loadURL('file://' + __dirname + '/index.html');
    mainWindow.loadURL('http://127.0.0.1:5000',{"extraHeaders" : "pragma: no-cache\n"});
    mainWindow.on('closed', function() {
      mainWindow = null;
      subpy.kill('SIGINT');
    });
  };

  var startUp = function(){
    rq(mainAddr)
      .then(function(htmlString){
        console.log('server started!');
        openWindow();
      })
      .catch(function(err){
        //console.log('waiting for the server start...');
        startUp();
      });
  };

  // fire!
  startUp();
});
