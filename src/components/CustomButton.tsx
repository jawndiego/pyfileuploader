import { ConnectKitButton } from "connectkit";
import { useRouter } from 'next/router';
import styled from "styled-components";
import { useEffect, useState } from 'react';

// FIX: we're currenly stuck in an endless loop with this code. 

const StyledButton = styled.button`
  cursor: pointer;
  position: relative;
  display: inline-block;
  padding: 14px 24px;
  color: #ffffff;
  background: #1a88f8;
  font-size: 16px;
  font-weight: 500;
  border-radius: 10rem;
  box-shadow: 0 4px 24px -6px #1a88f8;

  transition: 200ms ease;
  &:hover {
    transform: translateY(-6px);
    box-shadow: 0 6px 40px -6px #1a88f8;
  }
  &:active {
    transform: translateY(-3px);
    box-shadow: 0 6px 32px -6px #1a88f8;
  }
`;

interface CustomButtonProps {
  redirectTo: string;
}
export const CustomButton: React.FC<CustomButtonProps> = ({ redirectTo }) => {
    const router = useRouter();
    const [isConnected, setIsConnected] = useState(false);
    const [ensName, setEnsName] = useState("");
    const [truncatedAddress, setTruncatedAddress] = useState("");
    const [hasRedirected, setHasRedirected] = useState(false);
  
    // useEffect(() => {
    //   if (!isConnected && router.pathname !== '/' && !hasRedirected) {
    //     router.push('/');
    //     setHasRedirected(true);
    //   } else if (isConnected && router.pathname !== redirectTo && !hasRedirected) {
    //     router.push(redirectTo);
    //     setHasRedirected(true);
    //   }
    // }, [isConnected]);
  
    return (
      <ConnectKitButton.Custom>
        {({ isConnected: connected, show, truncatedAddress: address, ensName: name }) => {
          if (connected !== isConnected) {
            setIsConnected(connected);
            setEnsName(name ?? "");
            setTruncatedAddress(address ?? "");
            setHasRedirected(false);
          }
  
          return (
            <StyledButton onClick={show}>
              {isConnected ? ensName ?? truncatedAddress : "Connect Wallet"}
            </StyledButton>
          );
        }}
      </ConnectKitButton.Custom>
    );
  };
  