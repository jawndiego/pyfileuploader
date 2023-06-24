import { Header } from '../components'
import {useEffect, useState, useRef } from 'react'
import { useRouter } from 'next/router'

type MyDragEvent = React.DragEvent<HTMLDivElement>;


  function Page() {

	const [uploadSuccess, setUploadSuccess] = useState(false);
	const router = useRouter();

	const onDrop = async (acceptedFiles: File[]): Promise<void> => {
		try {
		  const data = new FormData();
		  
		  acceptedFiles.forEach((file, index) => {
			data.append(`file[]`, file); 
		  });
	  
		  const response = await fetch('upload', {
			method: 'POST',
			body: data
		  });
	  
		  if (response.ok) {
			console.log('All files uploaded successfully');
			setUploadSuccess(true);
			router.push('/chatbot')
		  } else {
			console.log('Upload failed');
		  }
		} catch (error) {
		  console.error('Error:', error);
		}
	  };

	const onFileChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
		if(event.target.files) {
		  const files = Array.from(event.target.files); // Convert FileList to Array
		  onDrop(files);
		}
	  }


	return (
	  <>
		<Header />

		<main className="flex min-h-screen flex-col items-center justify-between p-24">
		
          <div className="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10"
		    onDragOver={(event: MyDragEvent) => {
				// Prevent default behavior (Prevent file from being opened)
				event.preventDefault();
			  }}
			  onDrop={(event: MyDragEvent) => {
				event.preventDefault();
				const files: File[]= [];
			  if (event.dataTransfer.items) {
				for (let i = 0; i < event.dataTransfer.items.length; i++){
					if (event.dataTransfer.items[i].kind === 'file') {
						const file = event.dataTransfer.items[i].getAsFile();
						if (file !== null) {
							files.push(file);
						console.log('file', file);}
					}
				}
				onDrop(files);
			  }
			}}
			  >
            <div className="text-center">
              <svg className="mx-auto h-12 w-12 text-gray-300" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M1.5 6a2.25 2.25 0 012.25-2.25h16.5A2.25 2.25 0 0122.5 6v12a2.25 2.25 0 01-2.25 2.25H3.75A2.25 2.25 0 011.5 18V6zM3 16.06V18c0 .414.336.75.75.75h16.5A.75.75 0 0021 18v-1.94l-2.69-2.689a1.5 1.5 0 00-2.12 0l-.88.879.97.97a.75.75 0 11-1.06 1.06l-5.16-5.159a1.5 1.5 0 00-2.12 0L3 16.061zm10.125-7.81a1.125 1.125 0 112.25 0 1.125 1.125 0 01-2.25 0z" clip-rule="evenodd" />
              </svg>
              <div className="mt-4 flex text-sm leading-6 text-gray-600">
                <label htmlFor="file-upload" className="relative cursor-pointer rounded-md bg-white font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500">
                  <span>upload a file</span>
				  <input id="file-upload" name="file-upload" type="file" accept=".txt,.pdf" className="sr-only"
                  onChange={onFileChange}
                ></input>
                </label>
                <p className="pl-1">or drag and drop</p>
              </div>
              <p className="text-xs leading-5 text-gray-600">.txt or .pdf up to 10mb</p>
            </div>
          </div>
   

		</main>
	  </>
	);
  } 

  export default Page;