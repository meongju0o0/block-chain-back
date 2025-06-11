// SPDX-License-Identifier: MIT
pragma solidity >=0.8.2 <0.9.0;

contract CommentChain {
    struct Comment {
        uint256 commentId;
        uint256 paperId;      // 대상 논문 ID
        address reviewer;     // 리뷰어 지갑 주소
        string ipfsHash;      // IPFS에 저장된 댓글(리뷰) 원문 해시
        uint256 timestamp;    // 등록 시각
    }

    mapping(uint256 => Comment) public comments;

    mapping(uint256 => uint256[]) public paperComments;

    event CommentSubmitted(uint256 indexed commentId, uint256 indexed paperId, address indexed reviewer, string ipfsHash, uint256 timestamp);

    function submitComment(
        uint256 _commentId,
        uint256 _paperId,
        address _reviewer,
        string calldata _ipfsHash
    ) external {
        require(bytes(comments[_commentId].ipfsHash).length == 0, "Already Registered Comment.");

        comments[_commentId] = Comment({
            commentId: _commentId,
            paperId: _paperId,
            reviewer: _reviewer,
            ipfsHash: _ipfsHash,
            timestamp: block.timestamp
        });

        paperComments[_paperId].push(_commentId);

        emit CommentSubmitted(_commentId, _paperId, _reviewer, _ipfsHash, block.timestamp);
    }

    function getCommentsOfPaper(uint256 _paperId) external view returns (uint256[] memory) {
        return paperComments[_paperId];
    }

    function getComment(uint256 _commentId)
        external
        view
        returns (
            uint256,
            uint256,
            address,
            string memory,
            uint256
        )
    {
        Comment memory c = comments[_commentId];
        require(bytes(c.ipfsHash).length != 0, "Not Existed Comment.");
        return (c.commentId, c.paperId, c.reviewer, c.ipfsHash, c.timestamp);
    }
}