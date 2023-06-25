import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { Alchemy, Network } from "alchemy-sdk";
import { ConnectKitButton } from 'connectkit';
import axios from 'axios'; // You'll need to install axios: npm install axios

const CollectionPage: React.FC = () => {
  const [userAddress, setUserAddress] = useState<string | null>(null);
  const [nfts, setNfts] = useState<any[]>([]);
  const [nftsMeta, setMetadata] = useState<any[]>([]);

  // Setup: npm install alchemy-sdk
  const apiKey = process.env.NEXT_PUBLIC_ALCHEMY_KEY;
  const config = {
    apiKey: apiKey,
    network: Network.ETH_MAINNET,
  };
  const alchemy = new Alchemy(config);
  const v3url = `https://eth-mainnet.g.alchemy.com/nft/v3/${apiKey}/getNFTMetadata`;

  useEffect(() => {
    const fetchNfts = async () => {
      if (userAddress) {
        const nftsData = await alchemy.nft.getNftsForOwner(userAddress);
        setNfts(nftsData.ownedNfts); // Update the state with the fetched NFTs
  
        const nftsMetaData = await Promise.all(nftsData.ownedNfts.map(async nft => {
            const response = await axios.get(v3url, {
                params: {
                  contractAddress: nft.contract.address,
                  tokenId: nft.tokenId.toString(), // convert tokenId to string
                  tokenType: 'ERC721', // specify the token type
                  refreshCache: false
                }
              });
            return response.data;
          }));
        console.log(nftsMetaData); 
        setMetadata(nftsMetaData.filter(Boolean));
      }
    };
  
    fetchNfts();
  }, [userAddress]);
  

  return (
    <div>
      <Header redirectTo='/'/>
      <ConnectKitButton.Custom>
        {({ isConnected, show, address }) => {
          if (isConnected && address) {
            console.log("Connected address:", address); 
            setUserAddress(address);
          }
          return (
            <button onClick={show}>
              {isConnected ? address : "Connect Wallet"}
            </button>
          );
        }}
      </ConnectKitButton.Custom>
      <h1>Hello there</h1>
      {nfts.map((nft, index) => {
  return (
    <div key={index}>
      <h2>NFT #{index + 1}</h2>
      <p>Contract Address: {nft.contract.address}</p>
      <p>Token ID: {nft.tokenId}</p>
      <p>Balance: {nft.balance}</p>
      <p>Image Content Type: {nftsMeta[index]?.image?.contentType}</p> 
    </div>
  );
})}

    </div>
  );
};

export default CollectionPage;
