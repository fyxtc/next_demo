import Link from "next/link";
import Router from 'next/router'


export default class View extends React.Component {
  constructor(props){
    super(props)
    this.state = {
        data:null,
    };
  }
  componentDidMount() {
    fetch("http://localhost:5000/texts").then(resp => resp.json()).then(json => {
      console.log(json) 
      this.setState({data: json});
    })
  }

  render(){
    if(!this.state.data){
        return <p> loading </p>
    }else{
        return(
            this.state.data.map((data) =>
              <li key={data.tid}>{data.title} 

              <Link href={'/edit?id=' + data.tid}>
              <button type="button" value={data.tid}> edit </button>
              </Link>
              </li>
            )
        );

    }
  }

}
