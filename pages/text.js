import Router from 'next/router'


export default class Text extends React.Component {
  constructor(props){
    super(props)
    this.state = {
        title: null,
        content: null,
        isLock: false,
        isFound: true,
    };
  }

  static getInitialProps = ({query}) => {
    return {query}
  }

  componentDidMount() {
    var id = this.props.query.id
    let thiz = this
    fetch("http://localhost:5000/text/" + id).then(function(resp){
        console.log(resp)
        if (resp.status == 404){
            this.setState({isFound: false})
        }else{
            console.log("download >>>>>>>> " + id)
            var tempLink = document.createElement('a');
            tempLink.href = "http://localhost:5000/download/" + id;
            tempLink.click();
            return resp.json() 
        }
    }).then(data => {

            console.log(data)
            if(!data.isLock){
              thiz.setState({title: data.title});
              thiz.setState({content: data.content});
            }else{
              thiz.setState({isLock: data.isLock});
            }

    })
  }

    handleContentChange(e) {
        this.setState({ content: e.target.value });
    }

    handleSave() {
        console.log(this.state.title);
        console.log(this.state.content);
        fetch("http://localhost:5000/text/" + this.props.query.id, {
            method: "PUT",
            headers: {
                Accept: "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(this.state)
        }).then(() => {
            Router.push('/view')
        });
    }

  render(){
    if(!this.state.isLock){
        if(!this.state.content){
            return <p>loading</p>
        }else{
            return <div>
                <textarea
                    rows="3"
                    cols="20"
                    value={this.state.content}
                    onChange={this.handleContentChange.bind(this)}
                ></textarea>
                <button type="button" value={this.props.query.id} onClick={this.handleSave.bind(this)}> save </button>
            </div>
        }
        return <p>id: {this.props.query.id}</p>
    }else{
        return <p>current page is edited by other</p>
    }
  }
}


