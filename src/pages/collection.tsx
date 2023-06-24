import React, { useState, useEffect } from 'react';
import { Header } from '../components/Header';
import { Alchemy, Network } from "alchemy-sdk";
import { ConnectKitButton } from 'connectkit';

const CollectionPage: React.FC = () => {
  const [userAddress, setUserAddress] = useState<string | null>(null);

  // Setup: npm install alchemy-sdk
  const config = {
    apiKey: "INSERTAPIKEY",
    network: Network.ETH_MAINNET,
  };
  const alchemy = new Alchemy(config);

  useEffect(() => {
    const fetchNfts = async () => {
      if (userAddress) {
        const nfts = await alchemy.nft.getNftsForOwner(userAddress);
        console.log(nfts);
      }
    };

    fetchNfts();
  }, [userAddress]);

  return (
    <div>
      <Header />
      <ConnectKitButton.Custom>
        {({ isConnected, show, truncatedAddress: address }) => {
          if (isConnected && address) {
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
    </div>
  );
};

export default CollectionPage;
