import { Header } from '../components'
import {useEffect, useState} from 'react'

type MembersType = {
	members: string[];
  };
  
  function Page() {
	const [data, setData] = useState<MembersType | null>(null);
  
	useEffect(() => {
	  fetch("members")
		.then(response => {
		  if (!response.ok) {
			throw new Error("Error fetching data");
		  }
		  return response.json();
		})
		.then((data: MembersType) => setData(data))
		.catch((error) => console.error("Error:", error));
	}, []);
  
	if (!data) {
	  return (
		<>
		  <Header />
		  <p>Loading...</p>
		</>
	  );
	}
  
	return (
	  <>
		<Header />
		<main className="flex min-h-screen flex-col items-center justify-between p-24">
		  <div>
			{data.members.map((member, i) => (
			  <p key={i}>{member}</p>
			))}
		  </div>
		</main>
	  </>
	);
  }
  
  export default Page;
  