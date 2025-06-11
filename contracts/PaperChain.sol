// SPDX-License-Identifier: MIT
pragma solidity >=0.8.2 <0.9.0;

contract PaperChain {
    struct Paper {
        uint256 paperId;
        address submitter;   // 논문 등록자 주소
        string ipfsHash;     // IPFS에 저장된 논문 원문 해시
        uint256 timestamp;   // 등록 시각
    }

    mapping(uint256 => Paper) public papers;

    event PaperSubmitted(uint256 indexed paperId, address indexed submitter, string ipfsHash, uint256 timestamp);


    function submitPaper(uint256 _paperId, address _submitter, string calldata _ipfsHash) external {
        require(bytes(papers[_paperId].ipfsHash).length == 0, "Already Registered Paper.");

        papers[_paperId]= Paper({
            paperId: _paperId,
            submitter: _submitter,
            ipfsHash: _ipfsHash,
            timestamp: block.timestamp
        });
        emit PaperSubmitted(_paperId, _submitter, _ipfsHash, block.timestamp);
    }

    function getPaper(uint256 _paperId)
        external
        view
        returns (
            uint256,
            address,
            string memory,
            uint256
        )
    {
        Paper memory p = papers[_paperId];
        require(bytes(p.ipfsHash).length != 0, "Not Existed Paper.");
        return (p.paperId, p.submitter, p.ipfsHash, p.timestamp);
    }
}