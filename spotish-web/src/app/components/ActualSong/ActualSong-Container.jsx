import Author from "./Author";
import Cover from "./Cover";
import Title from "./Title";

export default ({ link, author, title}) => {    
  return (
    <div className="flex ">
        <Cover link={link}/>
        <div className="flex flex-col">
        <Title title={title}/>
        <Author author={author}/>
        </div>
    </div>
  );                      
};