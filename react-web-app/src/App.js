import React from 'react';

import './App.css';

import { Button, Card, Input, Typography } from 'antd';

class App extends React.Component {

  state = {
    statusData: ""
  };

  handleRefreshStatus = () => {
    fetch("http://localhost:5000/controller")
      .then(res => res.json())
      .then(data => this.setState({statusData: JSON.stringify(data, null, 4)}))
      .catch(err => alert(err))
  }

  handleChangeMode = (mode) => {
    fetch("http://localhost:5000/controller/mode", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({state: mode})})
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
            <Button type="primary" onClick={() => this.handleChangeMode("new")}>Change Mode New</Button>
          </Card>

        </div>

      </div>
    );
  }
}

export default App;
