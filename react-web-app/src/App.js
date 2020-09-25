import React from 'react';

import './App.css';

import { Button, Card, Input, Typography } from 'antd';
import ReactJson from 'react-json-view'

class App extends React.Component {

  state = {
    statusData: "",
    cavaConfig: {bruh: "bruh"}
  };

  //host = "http://raspberrypi:5000/controller"
  //host = "http://localhost:5000/controller"
  host = "192.168.1.12:5000/controller";

  handleRefreshStatus = () => {
    fetch(this.host)
      .then(res => res.json())
      .then(data => this.setState({statusData: JSON.stringify(data, null, 4)}))
      .catch(err => alert(err))
  }

  handleChangeMode = (mode) => {
    fetch(`${this.host}/mode/${mode}`, { method: "PUT" })
      .then(res => {
        if (res.status !== 202)
          alert("Change mode failed.")
        else
          this.handleRefreshStatus()
      })
      .catch(err => alert(err))
  }

  render() {
    return (
      <div className="App">

        <Typography.Title>rpi-controller</Typography.Title>

        <div className="Flex-container">

          <Card title="Status" style={{ width: 500, height: 270}}>
            <Button type="primary" onClick={this.handleRefreshStatus}>Refresh Status</Button>
            <p/>
            <Input.TextArea disabled value={this.state.statusData} rows={5} style={{resize: "none"}}></Input.TextArea>
          </Card>

          <Card title="Control" style={{ width: 500 }}>
            <Button type="primary" onClick={() => this.handleChangeMode("idle")}>Change Mode Idle</Button>
            <p/>
            <Button type="primary" onClick={() => this.handleChangeMode("pink")}>Change Mode Pink</Button>
            <p/>
            <Button type="primary" onClick={() => this.handleChangeMode("cava")}>Change Mode Cava</Button>
            <p/>
            <Typography.Paragraph strong>Cava Config</Typography.Paragraph>
            <ReactJson src={ this.state.cavaConfig } onEdit={(edit) => true} displayDataTypes={false} name={null} theme="ocean" style={{textAlign: "left"}}/>
          </Card>

        </div>

      </div>
    );
  }
}

export default App;
